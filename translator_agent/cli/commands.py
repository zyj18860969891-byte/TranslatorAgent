"""
CLI 命令定义

定义所有 CLI 命令和参数
"""

import asyncio
import logging
import click
from typing import Optional, List
from pathlib import Path

from ..core.translator import Translator
from ..core.modelscope_integration import ModelScopeClient
from ..data.video_processor import VideoProcessor
from ..data.subtitle_processor import SubtitleProcessor
from ..config.settings import ConfigManager

logger = logging.getLogger(__name__)

# 全局实例（延迟初始化）
config_manager = None
translator = None
modelscope_client = None
video_processor = None
subtitle_processor = None


def get_config_manager():
    """获取配置管理器实例"""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager()
    return config_manager


def get_translator():
    """获取翻译器实例"""
    global translator
    if translator is None:
        translator = Translator()
    return translator


def get_modelscope_client():
    """获取ModelScope客户端实例"""
    global modelscope_client
    if modelscope_client is None:
        modelscope_client = ModelScopeClient()
    return modelscope_client


def get_video_processor():
    """获取视频处理器实例"""
    global video_processor
    if video_processor is None:
        video_processor = VideoProcessor()
    return video_processor


def get_subtitle_processor():
    """获取字幕处理器实例"""
    global subtitle_processor
    if subtitle_processor is None:
        subtitle_processor = SubtitleProcessor()
    return subtitle_processor


@click.group()
@click.version_option(version="1.0.0")
@click.option('--config', '-c', type=click.Path(exists=True), help='配置文件路径')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']), default='INFO')
@click.pass_context
def cli(ctx, config, verbose, log_level):
    """Translator Agent CLI 工具"""
    ctx.ensure_object(dict)
    
    # 设置日志级别
    if verbose:
        log_level = 'DEBUG'
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 加载配置
    if config:
        get_config_manager().load_config(config)
    
    # 设置上下文对象
    ctx.obj['config'] = get_config_manager()
    ctx.obj['translator'] = get_translator()
    ctx.obj['modelscope_client'] = get_modelscope_client()
    ctx.obj['video_processor'] = get_video_processor()
    ctx.obj['subtitle_processor'] = get_subtitle_processor()


@cli.command()
@click.argument('text')
@click.option('--source', '-s', default='auto', help='源语言')
@click.option('--target', '-t', required=True, help='目标语言')
@click.option('--model', '-m', help='使用的模型')
@click.option('--temperature', type=float, default=0.7, help='生成温度')
@click.option('--max-tokens', type=int, default=1000, help='最大令牌数')
@click.pass_context
def translate(ctx, text, source, target, model, temperature, max_tokens):
    """文本翻译"""
    try:
        click.echo(f"正在翻译: {text}")
        click.echo(f"源语言: {source} -> 目标语言: {target}")
        
        from translator_agent.core.translator import TranslationRequest, Language, TranslationEngine
        
        translator = get_translator()
        request = TranslationRequest(
            text=text,
            source_lang=Language.ENGLISH if source == 'en' else Language.CHINESE,
            target_lang=Language.CHINESE if target == 'zh' else Language.ENGLISH,
            engine=TranslationEngine.CUSTOM
        )
        result = translator.translate(request)
        
        click.echo("\n翻译结果:")
        click.echo(f"原文: {text}")
        click.echo(f"译文: {result.translated_text}")
        click.echo(f"源语言: {result.source_lang.value}")
        click.echo(f"目标语言: {result.target_lang.value}")
        click.echo(f"引擎: {result.engine.value}")
        click.echo(f"置信度: {result.confidence:.2f}")
        if result.metadata:
            click.echo(f"元数据: {result.metadata}")
        
    except Exception as e:
        click.echo(f"翻译失败: {str(e)}", err=True)
        raise click.ClickException(str(e))


@cli.command()
@click.argument('video_path')
@click.option('--target', '-t', required=True, help='目标语言')
@click.option('--output', '-o', help='输出路径')
@click.option('--extract-frames', is_flag=True, help='提取视频帧')
@click.option('--process-subtitles', is_flag=True, default=True, help='处理字幕')
@click.option('--subtitle-path', help='字幕文件路径')
@click.option('--model', '-m', help='使用的模型')
@click.option('--temperature', type=float, default=0.7, help='生成温度')
@click.pass_context
def video_translate(ctx, video_path, target, output, extract_frames, process_subtitles, subtitle_path, model, temperature):
    """视频翻译"""
    async def _video_translate():
        try:
            video_path_obj = Path(video_path)
            if not video_path_obj.exists():
                raise click.ClickException(f"视频文件不存在: {video_path}")
            
            click.echo(f"正在处理视频: {video_path}")
            click.echo(f"目标语言: {target}")
            
            # 提取帧
            extracted_frames = []
            if extract_frames:
                click.echo("正在提取视频帧...")
                frames_dir = output or "frames"
                video_processor = get_video_processor()
                frames = await video_processor.extract_frames(
                    video_path=str(video_path_obj),
                    output_dir=frames_dir
                )
                extracted_frames = frames
                click.echo(f"已提取 {len(frames)} 帧")
            
            # 处理字幕
            translated_subtitles = None
            if process_subtitles:
                click.echo("正在处理字幕...")
                subtitle_processor = get_subtitle_processor()
                subtitle_result = await subtitle_processor.translate_video_subtitles(
                    video_path=str(video_path_obj),
                    target_language=target,
                    subtitle_path=subtitle_path,
                    output_path=output,
                    model_name=model,
                    temperature=temperature,
                    merge_segments=True
                )
                translated_subtitles = subtitle_result.get('output_path')
                if translated_subtitles:
                    click.echo(f"字幕翻译完成: {translated_subtitles}")
            
            click.echo("\n视频翻译完成!")
            click.echo(f"视频文件: {video_path}")
            if extracted_frames:
                click.echo(f"提取的帧: {len(extracted_frames)} 帧")
            if translated_subtitles:
                click.echo(f"翻译的字幕: {translated_subtitles}")
            
        except Exception as e:
            click.echo(f"视频翻译失败: {str(e)}", err=True)
            raise click.ClickException(str(e))
    
    asyncio.run(_video_translate())


@cli.command()
@click.argument('video_path')
@click.option('--output', '-o', help='输出路径')
@click.option('--frames-dir', help='帧输出目录')
@click.option('--frame-rate', type=float, default=2.0, help='帧率')
@click.option('--max-frames', type=int, default=100, help='最大帧数')
@click.pass_context
def extract_frames(ctx, video_path, output, frames_dir, frame_rate, max_frames):
    """提取视频帧"""
    async def _extract_frames():
        try:
            video_path_obj = Path(video_path)
            if not video_path_obj.exists():
                raise click.ClickException(f"视频文件不存在: {video_path}")
            
            click.echo(f"正在提取视频帧: {video_path}")
            click.echo(f"帧率: {frame_rate} fps")
            click.echo(f"最大帧数: {max_frames}")
            
            output_dir = frames_dir or output or "frames"
            video_processor = get_video_processor()
            
            frames = await video_processor.extract_frames(
                video_path=str(video_path_obj),
                output_dir=output_dir,
                frame_rate=frame_rate,
                max_frames=max_frames
            )
            
            click.echo(f"\n帧提取完成!")
            click.echo(f"视频文件: {video_path}")
            click.echo(f"输出目录: {output_dir}")
            click.echo(f"提取的帧: {len(frames)} 帧")
            
            # 显示前几帧的信息
            if frames:
                click.echo("\n前3帧信息:")
                for i, frame in enumerate(frames[:3]):
                    click.echo(f"  帧 {i+1}: {frame.timestamp:.2f}s -> {frame.frame_path}")
            
        except Exception as e:
            click.echo(f"帧提取失败: {str(e)}", err=True)
            raise click.ClickException(str(e))
    
    asyncio.run(_extract_frames())


@cli.command()
@click.argument('video_path')
@click.option('--output', '-o', help='输出路径')
@click.option('--subtitle-path', help='字幕文件路径')
@click.option('--model', '-m', help='使用的模型')
@click.pass_context
def extract_subtitles(ctx, video_path, output, subtitle_path, model):
    """提取视频字幕"""
    async def _extract_subtitles():
        try:
            video_path_obj = Path(video_path)
            if not video_path_obj.exists():
                raise click.ClickException(f"视频文件不存在: {video_path}")
            
            click.echo(f"正在提取字幕: {video_path}")
            
            output_path = output or f"{video_path_obj.stem}_subtitles.srt"
            video_processor = get_video_processor()
            modelscope_client = get_modelscope_client()
            
            # 提取字幕
            result = await video_processor.extract_subtitles_from_video(
                video_path=str(video_path_obj),
                output_path=output_path,
                model_client=modelscope_client
            )
            
            click.echo(f"\n字幕提取完成!")
            click.echo(f"视频文件: {video_path}")
            click.echo(f"字幕文件: {output_path}")
            click.echo(f"提取的字幕段: {len(result.get('subtitles', []))}")
            
            # 显示前几条字幕
            subtitles = result.get('subtitles', [])
            if subtitles:
                click.echo("\n前3条字幕:")
                for i, subtitle in enumerate(subtitles[:3]):
                    click.echo(f"  {i+1}. {subtitle['text']} ({subtitle['start_time']:.2f}s - {subtitle['end_time']:.2f}s)")
            
        except Exception as e:
            click.echo(f"字幕提取失败: {str(e)}", err=True)
            raise click.ClickException(str(e))
    
    asyncio.run(_extract_subtitles())


@cli.command()
@click.argument('video_path')
@click.option('--output', '-o', help='输出路径')
@click.option('--subtitle-path', help='字幕文件路径')
@click.option('--model', '-m', help='使用的模型')
@click.pass_context
def erase_subtitles(ctx, video_path, output, subtitle_path, model):
    """擦除视频字幕"""
    async def _erase_subtitles():
        try:
            video_path_obj = Path(video_path)
            if not video_path_obj.exists():
                raise click.ClickException(f"视频文件不存在: {video_path}")
            
            click.echo(f"正在擦除字幕: {video_path}")
            
            output_path = output or f"{video_path_obj.stem}_no_subtitles.mp4"
            video_processor = get_video_processor()
            modelscope_client = get_modelscope_client()
            
            # 擦除字幕
            result = await video_processor.erase_subtitles_from_video(
                video_path=str(video_path_obj),
                output_path=output_path,
                model_client=modelscope_client
            )
            
            click.echo(f"\n字幕擦除完成!")
            click.echo(f"原始视频: {video_path}")
            click.echo(f"处理后视频: {output_path}")
            click.echo(f"处理时间: {result.get('processing_time', 0):.2f}s")
            
        except Exception as e:
            click.echo(f"字幕擦除失败: {str(e)}", err=True)
            raise click.ClickException(str(e))
    
    asyncio.run(_erase_subtitles())


@cli.command()
@click.argument('subtitle_path')
@click.option('--target', '-t', required=True, help='目标语言')
@click.option('--output', '-o', help='输出路径')
@click.option('--source', '-s', default='auto', help='源语言')
@click.option('--model', '-m', help='使用的模型')
@click.pass_context
def translate_subtitles(ctx, subtitle_path, target, output, source, model):
    """翻译字幕文件"""
    async def _translate_subtitles():
        try:
            subtitle_path_obj = Path(subtitle_path)
            if not subtitle_path_obj.exists():
                raise click.ClickException(f"字幕文件不存在: {subtitle_path}")
            
            click.echo(f"正在翻译字幕: {subtitle_path}")
            click.echo(f"源语言: {source} -> 目标语言: {target}")
            
            output_path = output or f"{subtitle_path_obj.stem}_translated.srt"
            subtitle_processor = get_subtitle_processor()
            translator = get_translator()
            
            # 翻译字幕
            result = await subtitle_processor.process_srt_file(
                input_path=str(subtitle_path_obj),
                translator=translator,
                source_lang=source,
                target_lang=target
            )
            
            click.echo(f"\n字幕翻译完成!")
            click.echo(f"原始字幕: {subtitle_path}")
            click.echo(f"翻译字幕: {result}")
            
            # 显示统计信息
            stats = subtitle_processor.get_statistics()
            click.echo(f"\n统计信息:")
            click.echo(f"  总字幕段: {stats['total_segments']}")
            click.echo(f"  处理段数: {stats['processed_segments']}")
            click.echo(f"  失败段数: {stats['failed_segments']}")
            click.echo(f"  成功率: {stats['success_rate']:.2%}")
            click.echo(f"  处理时间: {stats.get('processing_time', 0):.2f}s")
            
        except Exception as e:
            click.echo(f"字幕翻译失败: {str(e)}", err=True)
            raise click.ClickException(str(e))
    
    asyncio.run(_translate_subtitles())


@cli.command()
@click.argument('subtitle_path')
@click.option('--target', '-t', required=True, help='目标语言')
@click.option('--output', '-o', help='输出路径')
@click.option('--model', '-m', help='使用的模型')
@click.option('--temperature', type=float, default=0.7, help='生成温度')
@click.option('--merge-segments', is_flag=True, default=True, help='合并字幕段')
@click.pass_context
def subtitle_translate(ctx, subtitle_path, target, output, model, temperature, merge_segments):
    """字幕翻译"""
    async def _subtitle_translate():
        try:
            subtitle_path_obj = Path(subtitle_path)
            if not subtitle_path_obj.exists():
                raise click.ClickException(f"字幕文件不存在: {subtitle_path}")
            
            click.echo(f"正在翻译字幕: {subtitle_path}")
            click.echo(f"目标语言: {target}")
            
            subtitle_processor = get_subtitle_processor()
            result = await subtitle_processor.translate_subtitles(
                subtitle_path=str(subtitle_path_obj),
                target_language=target,
                output_path=output,
                model_name=model,
                temperature=temperature,
                merge_segments=merge_segments
            )
            
            click.echo("\n字幕翻译完成!")
            click.echo(f"原始字幕: {subtitle_path}")
            click.echo(f"翻译字幕: {result['output_path']}")
            click.echo(f"字幕段数: {result['subtitle_count']}")
            click.echo(f"处理时间: {result['processing_time']:.2f}秒")
            
            if result.get('errors'):
                click.echo("\n警告:")
                for error in result['errors']:
                    click.echo(f"  - {error}")
            
        except Exception as e:
            click.echo(f"字幕翻译失败: {str(e)}", err=True)
            raise click.ClickException(str(e))
    
    asyncio.run(_subtitle_translate())


@cli.command()
@click.option('--model', '-m', help='指定模型')
@click.pass_context
def list_models(ctx, model):
    """列出可用模型"""
    async def _list_models():
        try:
            click.echo("正在获取可用模型...")
            
            modelscope_client = get_modelscope_client()
            models = await modelscope_client.list_models()
            
            if model:
                # 过滤特定模型
                filtered_models = [m for m in models if model.lower() in m.get('name', '').lower()]
                models = filtered_models
            
            if not models:
                click.echo("未找到可用模型")
                return
            
            click.echo(f"\n找到 {len(models)} 个可用模型:")
            click.echo("-" * 80)
            
            for model_info in models:
                name = model_info.get('name', 'Unknown')
                description = model_info.get('description', 'No description')
                languages = model_info.get('supported_languages', [])
                capabilities = model_info.get('capabilities', [])
                
                click.echo(f"名称: {name}")
                click.echo(f"描述: {description}")
                if languages:
                    click.echo(f"支持语言: {', '.join(languages)}")
                if capabilities:
                    click.echo(f"能力: {', '.join(capabilities)}")
                click.echo("-" * 80)
            
        except Exception as e:
            click.echo(f"获取模型列表失败: {str(e)}", err=True)
            raise click.ClickException(str(e))
    
    asyncio.run(_list_models())


@cli.command()
@click.pass_context
def health(ctx):
    """健康检查"""
    async def _health():
        try:
            click.echo("正在执行健康检查...")
            
            # 检查翻译服务
            try:
                from translator_agent.core.translator import TranslationRequest, Language, TranslationEngine
                translator = get_translator()
                request = TranslationRequest(
                    text="test",
                    source_lang=Language.ENGLISH,
                    target_lang=Language.CHINESE,
                    engine=TranslationEngine.CUSTOM
                )
                result = await translator.translate_async(request)
                if result.translated_text:
                    click.echo("[OK] 翻译服务: 正常")
                else:
                    click.echo(f"[ERROR] 翻译服务: 异常 - 翻译结果为空")
            except Exception as e:
                click.echo(f"[ERROR] 翻译服务: 异常 - {str(e)}")
            
            # 检查 ModelScope 服务
            try:
                modelscope_client = get_modelscope_client()
                await modelscope_client.list_models()
                click.echo("[OK] ModelScope 服务: 正常")
            except Exception as e:
                click.echo(f"[ERROR] ModelScope 服务: 异常 - {str(e)}")
            
            # 检查视频处理服务
            try:
                video_processor = get_video_processor()
                click.echo("[OK] 视频处理服务: 正常")
            except Exception as e:
                click.echo(f"✗ 视频处理服务: 异常 - {str(e)}")
            
            # 检查字幕处理服务
            try:
                subtitle_processor = get_subtitle_processor()
                click.echo("✓ 字幕处理服务: 正常")
            except Exception as e:
                click.echo(f"✗ 字幕处理服务: 异常 - {str(e)}")
            
            click.echo("\n健康检查完成!")
            
        except Exception as e:
            click.echo(f"健康检查失败: {str(e)}", err=True)
            raise click.ClickException(str(e))
    
    asyncio.run(_health())


@cli.command()
@click.pass_context
def config(ctx):
    """显示配置信息"""
    try:
        config_manager = get_config_manager()
        config_data = config_manager.get_config()
        
        click.echo("当前配置:")
        click.echo("-" * 40)
        
        for key, value in config_data.items():
            if isinstance(value, dict):
                click.echo(f"{key}:")
                for sub_key, sub_value in value.items():
                    click.echo(f"  {sub_key}: {sub_value}")
            else:
                click.echo(f"{key}: {value}")
        
        click.echo("-" * 40)
        
    except Exception as e:
        click.echo(f"获取配置失败: {str(e)}", err=True)
        raise click.ClickException(str(e))


# 便利命令
@cli.command()
@click.argument('text')
@click.option('--target', '-t', required=True, help='目标语言')
@click.pass_context
def quick_translate(ctx, text, target):
    """快速翻译（使用默认设置）"""
    ctx.invoke(translate, text=text, source='auto', target=target, model=None, temperature=0.7, max_tokens=1000)


@cli.command()
@click.argument('video_path')
@click.option('--target', '-t', required=True, help='目标语言')
@click.pass_context
def quick_video_translate(ctx, video_path, target):
    """快速视频翻译（使用默认设置）"""
    ctx.invoke(video_translate, video_path=video_path, target=target, output=None, 
              extract_frames=False, process_subtitles=True, subtitle_path=None, 
              model=None, temperature=0.7)



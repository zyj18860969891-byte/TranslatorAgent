import * as React from 'react';

interface DataTableProps {
  data: any[];
  columns: {
    key: string;
    header: string;
    render?: (value: any, row: any) => React.ReactNode;
  }[];
  className?: string;
}

const DataTable: React.FC<DataTableProps> = ({ data, columns, className }) => {
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full text-sm">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                className="px-4 py-3 text-left font-medium text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-gray-700"
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
          {data.map((row, index) => (
            <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
              {columns.map((column) => (
                <td
                  key={column.key}
                  className="px-4 py-3 text-gray-900 dark:text-gray-100"
                >
                  {column.render ? column.render(row[column.key], row) : row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export { DataTable };
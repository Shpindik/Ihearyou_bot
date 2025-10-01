import { SectionAnalyticsDto } from '@/entities/analytics';
import { FC } from 'react';

interface IProps {
  sections: SectionAnalyticsDto[];
}

const TopViews: FC<IProps> = ({ sections }) => {
  return (
    <div className="p-6 flex flex-col gap-4">
      <h2 className="mb-1">Топ-5 разделов по просмотрам</h2>

      {sections.slice(0, 5).map((section, index) => (
        <div key={section.id}>
          <p className="mb-1">
            {index + 1}. {section.title}
          </p>
          <div className="flex items-center gap-4">
            <div className="flex-1 h-8 bg-ui-gray-disabled rounded-full overflow-hidden">
              <div
                className="h-full bg-green-300 rounded-full transition-all duration-300"
                style={{ width: `${section.percentage}%` }}
              />
            </div>
            <p className="min-w-10 font-semibold">{section.percentage}%</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TopViews;

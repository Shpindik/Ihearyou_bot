import {
  MaterialAnalyticsDto,
  SectionAnalyticsDto,
} from '@/entities/analytics';
import { FC } from 'react';

interface IProps {
  materials: MaterialAnalyticsDto[];
  sections: SectionAnalyticsDto[];
}

const TopSummary: FC<IProps> = ({ materials, sections }) => {
  const materialsPercent = materials
    .slice(0, 5)
    .reduce((sum, material) => sum + material.percentage, 0);

  const sectionsPercent = sections
    .slice(0, 5)
    .reduce((sum, section) => sum + section.percentage, 0);

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="p-6 text-center">
        <h3 className="mb-2 text-ui-purple-primary font-bold">
          {materialsPercent}%
        </h3>

        <p>От всех просмотров приходится на топ-5 материалов</p>
      </div>
      <div className="p-6 text-center">
        <h3 className="mb-2 text-ui-purple-primary font-bold">
          {sectionsPercent}%
        </h3>

        <p>От всех просмотров приходится на топ-5 разделов</p>
      </div>
    </div>
  );
};

export default TopSummary;

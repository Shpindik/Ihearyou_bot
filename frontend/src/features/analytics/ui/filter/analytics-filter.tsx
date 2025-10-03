import { IAnalyticsRequest } from '@/entities/analytics';
import {
  PERIOD_OPTIONS,
  PeriodOptionType,
} from '@/entities/analytics/models/tuples';
import { PeriodType } from '@/entities/analytics/models/types';
import Dropdown from '@/shared/ui/dropdown';
import { FC } from 'react';

interface AnalyticsFilterProps {
  onFilterChange: (filters: IAnalyticsRequest) => void;
  className?: string;
}

const AnalyticsFilter: FC<AnalyticsFilterProps> = ({
  onFilterChange,
  className = '',
}) => {
  const handleOptionSelect = (option: PeriodOptionType) => {
    const filters: IAnalyticsRequest = {};

    if (option.value) {
      filters.period = option.value as PeriodType;
    }

    onFilterChange(filters);
  };

  return (
    <div className={`w-[10%] min-w-[150px] ${className}`}>
      <Dropdown<PeriodOptionType['value']>
        options={PERIOD_OPTIONS}
        placeholder="Выберите период"
        className="text-sm"
        onSelect={handleOptionSelect}
      />
    </div>
  );
};

export default AnalyticsFilter;

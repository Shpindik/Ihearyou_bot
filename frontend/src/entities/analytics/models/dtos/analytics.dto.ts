export interface AnalyticsDto {
  users: {
    total: number;
    new_users: number;
    active_today: number;
    active_week: number;
    active_month: number;
  };
  content: {
    total_views: number;
    average_views_per_day: number;
    top_materials: MaterialAnalyticsDto[];
    top_sections: SectionAnalyticsDto[];
  };
  ratings: {
    top_materials: MaterialRatingDto[];
    anti_top_materials: MaterialRatingDto[];
  };
  daily_views: DailyViewDto[];
}

export interface MaterialAnalyticsDto {
  id: number;
  title: string;
  count: number;
  percentage: number;
}

export interface SectionAnalyticsDto {
  id: number;
  title: string;
  count: number;
  percentage: number;
}

export interface MaterialRatingDto {
  id: number;
  title: string;
  rating: number;
  count: number;
}

export interface DailyViewDto {
  day: string;
  views: number;
}

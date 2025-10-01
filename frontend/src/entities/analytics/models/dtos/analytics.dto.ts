export interface AnalyticsDto {
  users: {
    total: number;
    active_today: number;
    active_week: number;
    active_month: number;
  };
  content: {
    total_menu_items: number;
    most_viewed: MaterialAnalyticsDto[];
    most_rated: MaterialRatingDto[];
  };
  activities: {
    total_views: number;
    total_downloads: number;
    total_ratings: number;
    search_queries: SearchQueryDto[];
  };
  questions: {
    total: number;
    pending: number;
    answered: number;
  };
}

export interface MaterialAnalyticsDto {
  id: number;
  title: string;
  view_count: number;
  download_count: number;
  average_rating: number;
}

export interface MaterialRatingDto {
  id: number;
  title: string;
  average_rating: number;
  rating_count: number;
}

export interface SearchQueryDto {
  query: string;
  count: number;
}

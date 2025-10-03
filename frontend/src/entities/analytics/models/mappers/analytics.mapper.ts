import {AnalyticsDto, IAnalyticsResponse} from '@/entities/analytics';

export const analyticsMapper = (
  response: IAnalyticsResponse | AnalyticsDto,
) => {
  console.log('analyticsMapper получил response:', response);

  if (!response) {
    return null;
  }

  return {
    users: {
      total: response.users.total,
      activeToday: response.users.active_today,
      activeWeek: response.users.active_week,
      activeMonth: response.users.active_month,
    },
    content: {
      totalMenuItems: response.content.total_menu_items,
      mostViewed: response.content.most_viewed.map((material) => ({
        id: material.id,
        title: material.title,
        view_count: material.view_count,
        download_count: material.download_count,
        average_rating: material.average_rating,
      })),
      mostRated: response.content.most_rated.map((material) => ({
        id: material.id,
        title: material.title,
        average_rating: material.average_rating,
        rating_count: material.rating_count,
      })),
    },
    activities: {
      totalViews: response.activities.total_views,
      totalDownloads: response.activities.total_downloads,
      totalRatings: response.activities.total_ratings,
      searchQueries: response.activities.search_queries.map((query) => ({
        query: query.query,
        count: query.count,
      })),
    },
    questions: {
      total: response.questions.total,
      pending: response.questions.pending,
      answered: response.questions.answered,
    },
  };
};

import { IAnalyticsResponse } from '../interfaces/analytics-response.interface';

export const analyticsMapper = (response: IAnalyticsResponse) => {
  console.log('analyticsMapper получил response:', response);

  if (!response) {
    return null;
  }

  return {
    users: {
      total: response.users.total,
      newUsers: response.users.new_users,
      activeToday: response.users.active_today,
      activeWeek: response.users.active_week,
      activeMonth: response.users.active_month,
    },
    content: {
      totalViews: response.content.total_views,
      averageViewsPerDay: response.content.average_views_per_day,
      topMaterials: response.content.top_materials.map((material) => ({
        id: material.id,
        title: material.title,
        count: material.count,
        percentage: material.percentage,
      })),
      topSections: response.content.top_sections.map((section) => ({
        id: section.id,
        title: section.title,
        count: section.count,
        percentage: section.percentage,
      })),
    },
    ratings: {
      topMaterials: response.ratings.top_materials.map((material) => ({
        id: material.id,
        title: material.title,
        rating: material.rating,
        count: material.count,
      })),
      antiTopMaterials: response.ratings.anti_top_materials.map((material) => ({
        id: material.id,
        title: material.title,
        rating: material.rating,
        count: material.count,
      })),
    },
    dailyViews: response.daily_views.map((view) => ({
      day: view.day,
      views: view.views,
    })),
  };
};

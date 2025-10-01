import { AnalyticsDto } from '@/entities/analytics';

export const analyticsMock: AnalyticsDto = {
  users: {
    total: 5263,
    active_today: 45,
    active_week: 320,
    active_month: 890,
  },
  content: {
    total_menu_items: 50,
    most_viewed: [
      {
        id: 1,
        title: 'История Дамбо',
        view_count: 1642,
        download_count: 234,
        average_rating: 4.9,
      },
      {
        id: 2,
        title: 'Как проходит проверка слуха',
        view_count: 1194,
        download_count: 189,
        average_rating: 4.8,
      },
      {
        id: 3,
        title: '10 мифов о потере слуха',
        view_count: 746,
        download_count: 156,
        average_rating: 4.7,
      },
      {
        id: 4,
        title: 'Подкаст «Влияние громкой музыки на слух»',
        view_count: 522,
        download_count: 98,
        average_rating: 4.66,
      },
      {
        id: 5,
        title: 'Декларация прав родителей',
        view_count: 224,
        download_count: 67,
        average_rating: 4.54,
      },
    ],
    most_rated: [
      {
        id: 1,
        title: 'История Дамбо',
        average_rating: 4.9,
        rating_count: 156,
      },
      {
        id: 2,
        title: 'Как проходит проверка слуха',
        average_rating: 4.8,
        rating_count: 134,
      },
      {
        id: 3,
        title: '10 мифов о потере слуха',
        average_rating: 4.7,
        rating_count: 98,
      },
      {
        id: 4,
        title: 'Подкаст «Влияние громкой музыки на слух»',
        average_rating: 4.66,
        rating_count: 87,
      },
      {
        id: 5,
        title: 'Декларация прав родителей',
        average_rating: 4.54,
        rating_count: 76,
      },
      {
        id: 6,
        title: 'Сложные случаи слухопротезирования',
        average_rating: 1.1,
        rating_count: 23,
      },
      {
        id: 7,
        title: 'Технические характеристики аппаратов',
        average_rating: 2.1,
        rating_count: 45,
      },
      {
        id: 8,
        title: 'История развития слуховых аппаратов',
        average_rating: 2.6,
        rating_count: 34,
      },
      {
        id: 9,
        title: 'Сравнение производителей',
        average_rating: 2.9,
        rating_count: 67,
      },
      {
        id: 10,
        title: 'Финансовые аспекты лечения',
        average_rating: 3.3,
        rating_count: 89,
      },
    ],
  },
  activities: {
    total_views: 5420,
    total_downloads: 890,
    total_ratings: 340,
    search_queries: [
      {
        query: 'слуховые аппараты',
        count: 45,
      },
      {
        query: 'проверка слуха',
        count: 32,
      },
      {
        query: 'потеря слуха',
        count: 28,
      },
      {
        query: 'реабилитация',
        count: 19,
      },
      {
        query: 'детский слух',
        count: 15,
      },
    ],
  },
  questions: {
    total: 150,
    pending: 25,
    answered: 125,
  },
};

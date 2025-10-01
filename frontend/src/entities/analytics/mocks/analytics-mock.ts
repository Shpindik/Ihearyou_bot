import { AnalyticsDto } from '../models/dtos/analytics.dto';

export const analyticsMock: AnalyticsDto = {
  users: {
    total: 5263,
    new_users: 1421,
    active_today: 45,
    active_week: 320,
    active_month: 890,
  },
  content: {
    total_views: 7464,
    average_views_per_day: 578,
    top_materials: [
      {
        id: 1,
        title: 'История Дамбо',
        view_count: 1642,
        percentage: 22,
      },
      {
        id: 2,
        title: 'Как проходит проверка слуха',
        view_count: 1194,
        percentage: 16,
      },
      {
        id: 3,
        title: '10 мифов о потере слуха',
        view_count: 746,
        percentage: 10,
      },
      {
        id: 4,
        title: 'Подкаст «Влияние громкой музыки на слух»',
        view_count: 522,
        percentage: 7,
      },
      {
        id: 5,
        title: 'Декларация прав родителей',
        view_count: 224,
        percentage: 3,
      },
    ],
    top_sections: [
      {
        id: 1,
        title: 'Эмоции и принятие',
        view_count: 2239,
        percentage: 30,
      },
      {
        id: 2,
        title: 'Юридическая информация',
        view_count: 1642,
        percentage: 22,
      },
      {
        id: 3,
        title: 'Советы психолога',
        view_count: 1119,
        percentage: 15,
      },
      {
        id: 4,
        title: 'Жизнь с особенностями слуха',
        view_count: 522,
        percentage: 7,
      },
      {
        id: 5,
        title: 'Поддержка в школе и общении',
        view_count: 75,
        percentage: 1,
      },
    ],
  },
  ratings: {
    top_materials: [
      {
        id: 1,
        title: 'История Дамбо',
        rating: 4.9,
        rating_count: 156,
      },
      {
        id: 2,
        title: 'Как проходит проверка слуха',
        rating: 4.8,
        rating_count: 134,
      },
      {
        id: 3,
        title: '10 мифов о потере слуха',
        rating: 4.7,
        rating_count: 98,
      },
      {
        id: 4,
        title: 'Подкаст «Влияние громкой музыки на слух»',
        rating: 4.66,
        rating_count: 87,
      },
      {
        id: 5,
        title: 'Декларация прав родителей',
        rating: 4.54,
        rating_count: 76,
      },
    ],
    anti_top_materials: [
      {
        id: 6,
        title: 'Сложные случаи слухопротезирования',
        rating: 1.1,
        rating_count: 23,
      },
      {
        id: 7,
        title: 'Технические характеристики аппаратов',
        rating: 2.1,
        rating_count: 45,
      },
      {
        id: 8,
        title: 'История развития слуховых аппаратов',
        rating: 2.6,
        rating_count: 34,
      },
      {
        id: 9,
        title: 'Сравнение производителей',
        rating: 2.9,
        rating_count: 67,
      },
      {
        id: 10,
        title: 'Финансовые аспекты лечения',
        rating: 3.3,
        rating_count: 89,
      },
    ],
  },
  daily_views: [
    {
      day: 'ПН',
      views: 648,
    },
    {
      day: 'ВТ',
      views: 420,
    },
    {
      day: 'СР',
      views: 380,
    },
    {
      day: 'ЧТ',
      views: 520,
    },
    {
      day: 'ПТ',
      views: 680,
    },
    {
      day: 'СБ',
      views: 320,
    },
    {
      day: 'ВС',
      views: 280,
    },
  ],
};


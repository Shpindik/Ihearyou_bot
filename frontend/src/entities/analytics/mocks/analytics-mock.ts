import { AnalyticsDto, PeriodType } from '@/entities/analytics';

// Базовые материалы с акцентом на детский слух - много вариантов
const baseMaterials = [
  // Детский слух - топ материалы
  {
    id: 1,
    title: 'Развитие слуха у детей: от рождения до 3 лет',
    view_count: 2847,
    download_count: 456,
    average_rating: 4.9,
  },
  {
    id: 2,
    title: 'Как проверить слух ребенка в домашних условиях',
    view_count: 2156,
    download_count: 389,
    average_rating: 4.8,
  },
  {
    id: 3,
    title: 'Слуховые аппараты для детей: особенности выбора',
    view_count: 1987,
    download_count: 312,
    average_rating: 4.7,
  },
  {
    id: 4,
    title: 'Реабилитация слуха у детей после кохлеарной имплантации',
    view_count: 1654,
    download_count: 278,
    average_rating: 4.6,
  },
  {
    id: 5,
    title: 'Игры для развития слухового восприятия у детей',
    view_count: 1432,
    download_count: 234,
    average_rating: 4.5,
  },
  {
    id: 6,
    title: 'Признаки нарушения слуха у младенцев',
    view_count: 1287,
    download_count: 198,
    average_rating: 4.4,
  },
  {
    id: 7,
    title: 'Слуховая терапия для детей с аутизмом',
    view_count: 1156,
    download_count: 167,
    average_rating: 4.3,
  },
  {
    id: 8,
    title: 'Музыкальная терапия для развития слуха у детей',
    view_count: 987,
    download_count: 145,
    average_rating: 4.2,
  },
  {
    id: 9,
    title: 'Слуховые аппараты для школьников: адаптация и поддержка',
    view_count: 876,
    download_count: 123,
    average_rating: 4.1,
  },
  {
    id: 10,
    title: 'Роль родителей в развитии слуха ребенка',
    view_count: 765,
    download_count: 98,
    average_rating: 4.0,
  },
  // Дополнительные материалы по детскому слуху
  {
    id: 11,
    title: 'Кохлеарная имплантация у детей: показания и противопоказания',
    view_count: 654,
    download_count: 87,
    average_rating: 3.9,
  },
  {
    id: 12,
    title: 'Слуховые аппараты для новорожденных',
    view_count: 543,
    download_count: 76,
    average_rating: 3.8,
  },
  {
    id: 13,
    title: 'Развитие речи у детей с нарушением слуха',
    view_count: 432,
    download_count: 65,
    average_rating: 3.7,
  },
  {
    id: 14,
    title: 'Слуховая диагностика у детей раннего возраста',
    view_count: 321,
    download_count: 54,
    average_rating: 3.6,
  },
  {
    id: 15,
    title: 'Слуховые аппараты для подростков: психологические аспекты',
    view_count: 210,
    download_count: 43,
    average_rating: 3.5,
  },
  // Общие материалы по слуху
  {
    id: 16,
    title: 'Слуховые аппараты: типы и характеристики',
    view_count: 1898,
    download_count: 298,
    average_rating: 4.2,
  },
  {
    id: 17,
    title: 'Проверка слуха: методы и процедуры',
    view_count: 1654,
    download_count: 234,
    average_rating: 4.1,
  },
  {
    id: 18,
    title: 'Потеря слуха: причины и профилактика',
    view_count: 1432,
    download_count: 187,
    average_rating: 4.0,
  },
  {
    id: 19,
    title: 'Реабилитация слуха у взрослых',
    view_count: 1234,
    download_count: 156,
    average_rating: 3.9,
  },
  {
    id: 20,
    title: 'Слуховые аппараты: настройка и обслуживание',
    view_count: 987,
    download_count: 123,
    average_rating: 3.8,
  },
  // Материалы с низкими рейтингами (антитоп)
  {
    id: 21,
    title: 'Сложные случаи слухопротезирования',
    view_count: 234,
    download_count: 23,
    average_rating: 1.1,
  },
  {
    id: 22,
    title: 'Технические характеристики аппаратов',
    view_count: 345,
    download_count: 45,
    average_rating: 2.1,
  },
  {
    id: 23,
    title: 'История развития слуховых аппаратов',
    view_count: 456,
    download_count: 34,
    average_rating: 2.6,
  },
  {
    id: 24,
    title: 'Сравнение производителей',
    view_count: 567,
    download_count: 67,
    average_rating: 2.9,
  },
  {
    id: 25,
    title: 'Финансовые аспекты лечения',
    view_count: 678,
    download_count: 89,
    average_rating: 3.3,
  },
  {
    id: 26,
    title: 'Устаревшие методы лечения слуха',
    view_count: 123,
    download_count: 12,
    average_rating: 1.5,
  },
  {
    id: 27,
    title: 'Непроверенные народные средства',
    view_count: 89,
    download_count: 8,
    average_rating: 1.8,
  },
  {
    id: 28,
    title: 'Слуховые аппараты низкого качества',
    view_count: 156,
    download_count: 15,
    average_rating: 2.3,
  },
  {
    id: 29,
    title: 'Неправильная диагностика слуха',
    view_count: 234,
    download_count: 22,
    average_rating: 2.7,
  },
  {
    id: 30,
    title: 'Проблемы с настройкой аппаратов',
    view_count: 345,
    download_count: 33,
    average_rating: 2.8,
  },
];

// Данные для разных периодов
const periodData = {
  day: {
    users: { total: 45, active_today: 45, active_week: 45, active_month: 45 },
    activities: {
      total_views: 542,
      total_downloads: 89,
      total_ratings: 34,
      search_queries: [
        { query: 'детский слух', count: 4 },
        { query: 'слуховые аппараты для детей', count: 3 },
        { query: 'проверка слуха ребенка', count: 2 },
        { query: 'развитие слуха у детей', count: 1 },
        { query: 'реабилитация слуха детей', count: 1 },
      ],
    },
    questions: { total: 15, pending: 3, answered: 12 },
  },
  week: {
    users: {
      total: 320,
      active_today: 45,
      active_week: 320,
      active_month: 320,
    },
    activities: {
      total_views: 1626,
      total_downloads: 267,
      total_ratings: 102,
      search_queries: [
        { query: 'детский слух', count: 13 },
        { query: 'слуховые аппараты для детей', count: 10 },
        { query: 'проверка слуха ребенка', count: 8 },
        { query: 'развитие слуха у детей', count: 6 },
        { query: 'реабилитация слуха детей', count: 5 },
      ],
    },
    questions: { total: 45, pending: 8, answered: 37 },
  },
  month: {
    users: {
      total: 890,
      active_today: 45,
      active_week: 320,
      active_month: 890,
    },
    activities: {
      total_views: 3794,
      total_downloads: 623,
      total_ratings: 238,
      search_queries: [
        { query: 'детский слух', count: 32 },
        { query: 'слуховые аппараты для детей', count: 25 },
        { query: 'проверка слуха ребенка', count: 20 },
        { query: 'развитие слуха у детей', count: 15 },
        { query: 'реабилитация слуха детей', count: 12 },
      ],
    },
    questions: { total: 105, pending: 18, answered: 87 },
  },
  year: {
    users: {
      total: 5263,
      active_today: 45,
      active_week: 320,
      active_month: 890,
    },
    activities: {
      total_views: 5420,
      total_downloads: 890,
      total_ratings: 340,
      search_queries: [
        { query: 'детский слух', count: 45 },
        { query: 'слуховые аппараты для детей', count: 32 },
        { query: 'проверка слуха ребенка', count: 28 },
        { query: 'развитие слуха у детей', count: 19 },
        { query: 'реабилитация слуха детей', count: 15 },
      ],
    },
    questions: { total: 150, pending: 25, answered: 125 },
  },
  all: {
    users: {
      total: 5263,
      active_today: 45,
      active_week: 320,
      active_month: 890,
    },
    activities: {
      total_views: 5420,
      total_downloads: 890,
      total_ratings: 340,
      search_queries: [
        { query: 'детский слух', count: 45 },
        { query: 'слуховые аппараты для детей', count: 32 },
        { query: 'проверка слуха ребенка', count: 28 },
        { query: 'развитие слуха у детей', count: 19 },
        { query: 'реабилитация слуха детей', count: 15 },
      ],
    },
    questions: { total: 150, pending: 25, answered: 125 },
  },
};

// Функция для получения моков в зависимости от периода
export const getAnalyticsMock = (period?: PeriodType): AnalyticsDto => {
  const periodKey = period || 'all';
  const data = periodData[periodKey];

  // Фильтруем материалы в зависимости от периода
  let filteredMaterials = baseMaterials;
  if (period === 'day') {
    filteredMaterials = baseMaterials.slice(0, 5); // Только топ-5 за день
  } else if (period === 'week') {
    filteredMaterials = baseMaterials.slice(0, 10); // Топ-10 за неделю
  } else if (period === 'month') {
    filteredMaterials = baseMaterials.slice(0, 15); // Топ-15 за месяц
  }

  // Для антитопа берем материалы с низким рейтингом
  const lowRatedMaterials = [...filteredMaterials]
    .filter((material) => material.average_rating < 3.0)
    .sort((a, b) => a.average_rating - b.average_rating); // Сортируем от низкого к высокому

  return {
    users: data.users,
    content: {
      total_menu_items: Math.round(
        50 *
          (period === 'day'
            ? 0.1
            : period === 'week'
              ? 0.3
              : period === 'month'
                ? 0.7
                : 1),
      ),
      most_viewed: filteredMaterials.slice(0, 10).map((material, index) => ({
        ...material,
        view_count: Math.round(
          material.view_count *
            (period === 'day'
              ? 0.1
              : period === 'week'
                ? 0.3
                : period === 'month'
                  ? 0.7
                  : 1),
        ),
        download_count: Math.round(
          material.download_count *
            (period === 'day'
              ? 0.1
              : period === 'week'
                ? 0.3
                : period === 'month'
                  ? 0.7
                  : 1),
        ),
        average_rating: Math.max(3.0, material.average_rating - index * 0.05),
      })),
      most_rated: lowRatedMaterials.slice(0, 10).map((material, index) => ({
        id: material.id,
        title: material.title,
        average_rating: material.average_rating, // Используем реальный рейтинг
        rating_count: Math.round(
          (100 + index * 20) *
            (period === 'day'
              ? 0.1
              : period === 'week'
                ? 0.3
                : period === 'month'
                  ? 0.7
                  : 1),
        ),
      })),
    },
    activities: data.activities,
    questions: data.questions,
  };
};

// Экспорт для обратной совместимости
export const analyticsMock = getAnalyticsMock();

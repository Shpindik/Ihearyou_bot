import { UserDetailsResponseDto } from '../dtos';

export const userDetailsMapper = (dto: UserDetailsResponseDto) => {
  return {
    id: dto.id,
    telegramId: dto.telegram_id,
    username: dto.username,
    firstName: dto.first_name,
    lastName: dto.last_name,
    subscriptionType: dto.subscription_type,
    lastActivity: dto.last_activity,
    reminderSentAt: dto.reminder_sent_at,
    createdAt: dto.created_at,
    activitiesCount: dto.activities_count,
    questionsCount: dto.questions_count,
  };
};

import { TemplateItemDto, TemplatesListDto } from '../dtos';

export const templateItemMapper = (dto: TemplateItemDto) => ({
  id: dto.id,
  name: dto.name,
  messageTemplate: dto.message_template,
  isActive: dto.is_active,
  createdAt: dto.created_at,
  updatedAt: dto.updated_at,
});

export const templateListMapper = (response: { list: TemplatesListDto }) => {
  if (!response?.list?.items) return { items: [], total: 0 };

  return {
    items: response.list.items.map(templateItemMapper),
    total: response.list.items.length,
  };
};

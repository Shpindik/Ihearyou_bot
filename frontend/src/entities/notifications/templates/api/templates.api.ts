import {templateListMapper, templatesListMock, TTemplateItem,} from '@/entities/notifications';
import {api} from '@/shared/api';

export const getTemplatesList = async (): Promise<{
  items: TTemplateItem[];
  total: number;
}> => {
  return api
    .get('/v1/admin/reminder-templates')
    .then((response) => {
      return response.data;
    })
    .then(templateListMapper)
    .catch((e) => {
      console.log('API недоступен, используем моки:', e);
      return templateListMapper({ list: templatesListMock });
    });
};

export const createTemplate = async (data: any): Promise<TTemplateItem> => {
  return api
    .post('/v1/admin/reminder-templates', data)
    .then((response) => response.data);
};

export const updateTemplate = async (
  id: number,
  data: any,
): Promise<TTemplateItem> => {
  return api
    .put(`/v1/admin/reminder-templates/${id}`, data)
    .then((response) => response.data);
};

export const deleteTemplate = async (id: number): Promise<void> => {
  return api.delete(`/v1/admin/reminder-templates/${id}`).then(() => {});
};

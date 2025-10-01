import { IListItem } from '@/entities/user/list';

export interface UserListDto {
  items: IListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

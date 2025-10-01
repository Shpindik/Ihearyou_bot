import { UserItemDto } from './user-item.dto';

export interface UserListDto {
  items: UserItemDto[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

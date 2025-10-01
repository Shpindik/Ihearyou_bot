import { TUserDetailsItem, userDetailsMapper } from '@/entities/user/details';
import { UserDetailsResponseDto } from '@/entities/user/details/models/dtos/user-details-response.dto';
import { IUserDetailsRequest } from '@/entities/user/details/models/interfaces/user-details-request.interface';
import { api } from '@/shared/api';

export const getUserDetails = async (
  params: IUserDetailsRequest,
): Promise<TUserDetailsItem> => {
  return api
    .get<UserDetailsResponseDto>(`/admin/telegram-users/${params.id}`, {
      baseURL: import.meta.env.VITE_API_URL,
    })
    .then((response) => response.data)
    .then(userDetailsMapper)
    .catch((e) => {
      console.log(e);
      return {} as TUserDetailsItem;
    });
};

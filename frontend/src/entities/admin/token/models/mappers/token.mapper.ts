import {IToken, ITokenResponse} from '../interfaces';

export const tokenMapper = (response: ITokenResponse): IToken => ({
  access: response.access_token.access_token,
  refresh: response.refresh_token.refresh_token,
  type: response.token_type.token_type,
  expires_in: response.expires_in.expires_in,
});

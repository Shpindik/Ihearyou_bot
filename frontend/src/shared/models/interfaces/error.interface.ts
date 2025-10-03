/**
 * @example
 * {
 *   "success": false,
 *   "error": {
 *     "code": "VALIDATION_ERROR",
 *     "message": "Ошибка валидации данных",
 *     "details": [
 *       {
 *         "field": "title",
 *         "message": "Поле обязательно для заполнения"
 *       }
 *     ]
 *   }
 * }
 */

export interface IError {
  success: boolean;
  error: {
    code: string;
    message: string;
    details: [
      {
        field: string;
        message: string;
      },
    ];
  };
}

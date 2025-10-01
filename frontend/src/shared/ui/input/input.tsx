import {ComponentPropsWithoutRef, forwardRef, ReactNode} from 'react';
import {MPaddingPostfix, MPaddingPrefix, MPositionPostfix, MPositionPrefix, MSize, TSize,} from './models';

interface IProps extends Omit<ComponentPropsWithoutRef<'input'>, 'prefix'> {
  sizes?: TSize;
  prefix?: ReactNode;
  postfix?: ReactNode;
  error?: boolean;
}

const UIInput = forwardRef<HTMLInputElement, IProps>(
  (
    { sizes = 'M', error = false, prefix, postfix, className, ...props },
    ref,
  ) => {
    return (
      <div className="relative w-full">
        {prefix && (
          <div className={`absolute ${MPositionPrefix[sizes]}`}>{prefix}</div>
        )}

        <input
          ref={ref}
          className={`input-focus ${className} ${MSize[sizes]} ${error ? 'input-error' : ''} 
                      ${prefix ? `${MPaddingPrefix[sizes]}` : ''}
                      ${postfix ? `${MPaddingPostfix[sizes]}` : ''}`}
          {...props}
        />

        {postfix && (
          <div className={`absolute ${MPositionPostfix[sizes]}`}>{postfix}</div>
        )}
      </div>
    );
  },
);

export default UIInput;

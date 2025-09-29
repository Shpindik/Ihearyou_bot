import { ComponentPropsWithoutRef, FC } from 'react';

interface IProps extends ComponentPropsWithoutRef<'div'> {
  text?: string;
  background?: boolean;
  block?: boolean;
}

const UIFullBackdropLoader: FC<IProps> = ({
  text,
  background,
  block,
  className = '',
  ...props
}) => {
  return (
    <div
      className={`${className} absolute inset-0 flex-center flex-col gap-r-3 transition-all z-20 ${background ? 'bg-black/[0.48] backdrop-blur-sm' : ''} ${
        block ? 'cursor-not-allowed' : 'pointer-events-none'
      }`}
      {...props}
    >
      <div className="w-12 h-12 p-r-2 bg-black/[0.52] rounded-full">
        <div className="full-size rounded-full border-[3px] border-white border-x-transparent animate-loader-spin"></div>
      </div>

      {!!text && (
        <div className="bg-black/[0.52] rounded-lg max-w-full font-semibold py-ui-1 px-r-3 text-r-sm text-white">
          {text}
        </div>
      )}
    </div>
  );
};

export default UIFullBackdropLoader;

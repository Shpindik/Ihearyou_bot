import {ComponentPropsWithoutRef, FC} from 'react';
import Icon from './icon';
import {EErrors} from '@/pages/error/ui/models';
import {MButtonTitles, MCodes, MDescriptions, MTitles} from './models';
import {UIButton} from '@/shared/ui';

interface IProps extends ComponentPropsWithoutRef<'div'> {
  error: EErrors;
  onButtonClick: () => void;
}

const ErrorMessage: FC<IProps> = ({
  className,
  error,
  onButtonClick,
  ...props
}) => {
  return (
    <div
      className={`${className} flex-center flex-col gap-3 text-ui-black-primary text-center`}
      {...props}
    >
      <Icon error={error} className="text-ui-gray-text-additional" />
      <h1>{MCodes[error]}</h1>

      <h2>{MTitles[error]}</h2>

      <p>{MDescriptions[error]}</p>

      <UIButton
        className="w-full mt-6 truncate"
        theme="primary-fill"
        size="S"
        onClick={onButtonClick}
      >
        {MButtonTitles[error]}
      </UIButton>
    </div>
  );
};

export default ErrorMessage;

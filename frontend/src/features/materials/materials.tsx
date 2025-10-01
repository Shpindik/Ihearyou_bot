import { ComponentPropsWithoutRef, FC } from 'react';

export const Materials: FC<ComponentPropsWithoutRef<'div'>> = ({
  className,
}) => {
  return (
    <div className={`${className} w-full flex flex-col h-full`}>
      <div className="p-4">
        <h1>Раздел Материалов</h1>
      </div>

      <div className="flex-1 min-h-0 overflow-auto scrollbar-hide">
        <div className="w-full pb-8">
          {/* Контент материалов будет здесь */}
        </div>
      </div>
    </div>
  );
};

export default Materials;

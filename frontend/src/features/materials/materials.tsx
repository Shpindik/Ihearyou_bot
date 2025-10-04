import { UIBlock } from '@/shared/ui';
// import Dropdown from '@/shared/ui/dropdown/dropdown';
import { ArrowIcon, CloseIcon, EditIcon } from '@/shared/svg';
import { Dropdown } from '@/shared/ui/dropdown/dropdown';
import { ComponentPropsWithoutRef, FC } from 'react';
import CreateNotification from '../notifications/ui/create-notification/create-notification';


export const Materials: FC<ComponentPropsWithoutRef<'div'>> = ({
  className,
}) => {
  const handleCreate = () => {
    console.log('Создать новый узел');
  };
  
const options = [
    { value: 'option1', label: 'Первый вариант' },
    { value: 'option2', label: 'Второй вариант' },
    { value: 'option3', label: 'Третий вариант' },
  ];

 const materials = [
    {
      title: 'Как начать',
      url: 'https://www.ihearyou.ru/materials/articles/kak-nachinat',
    },
    {
      title: 'Общение и слухопротезирование',
      url: 'https://www.ihearyou.ru/materials/articles/pervye-shagi-kommunikatsiya-slukhoprotezirovanie',
    },
    {
      title: 'От родителей родителям',
      url: 'https://ihearyou.ru/materials/skoraya-pomoshch-ot-roditeley-roditeleyam/skoraya-pomoshch-ot-roditeley-roditeleyam',
    },
  ];
  
  return (
    <div className={`${className} w-full flex flex-col h-full`}>
      <div className="p-4">
        <h1>Материалы</h1>
      </div>

      <div className="flex-1 overflow-auto scrollbar-hide">
        <div className="w-full pb-8">
          {/* Контент материалов будет здесь */}
                <div className="flex flex-wrap gap-6 px-7 py-6">
                  <UIBlock className='flex-1 max-w-[800px] px-5 py-6'>Приветственное сообщение
                    <p className="py-3">Здравствуйте! Мы рядом, чтобы помочь вам разобраться с вопросами, связанными со слухом. Если вы беспокоитесь о своём слухе или слухе вашего ребёнка, мы поможем оценить ситуацию. Вы сможете проверить слух, получить советы специалистов и найти истории людей, которые столкнулись с проблемами со слухом. О чьём слухе вы волнуетесь?</p>
                  </UIBlock>
                  {/* создаём узел */}
                  <CreateNotification
                    onClick={handleCreate}
                    className="flex-1 max-w-[400px]"
                    />
                </div>
               
          
                {/* Список созданных узлов */}
          <div className="flex flex-row gap-6 px-7 h-full">
                {/* Dropdown  */}
            <div className=" w-full sm:w-[300px] md:w-[350px] lg:w-[400px]">
             <Dropdown
             className='bg-ui-green-primary'
               options={options}
                placeholder="Выберите вариант"
                icon={<ArrowIcon />}
                
              />
            </div>
            <UIBlock className="mw-800px px-7 mt-4 p-6">
              {/* Заголовки колонок */}
              <div className="grid grid-cols-[2fr_3fr_1fr] pb-3 mb-3 font-medium">
                <span>Название</span>
                <span>URL</span>
                <span className="text-right">Действия</span>
              </div>

              {/* Строки */}
              <div className="space-y-3">
                {materials.map((item) => (
                  <div
                    key={item.title}
                    className="grid grid-cols-[2fr_3fr_1fr] grid-auto-flow items-center py-2"
                  >
                    <span>{item.title}</span>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-600 hover:underline truncate"
                    >
                      {item.url}
                    </a>
                    <div className="flex items-center gap-4 justify-end pr-2">
                      <button className="p-2 rounded-full hover:bg-gray-100 transition flex items-center justify-center">
                      <EditIcon className='w-5 h-5' />
                      </button>
                      <button className="hover:opacity-70 transition">
                        <CloseIcon w-5 h-5 />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </UIBlock>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Materials;

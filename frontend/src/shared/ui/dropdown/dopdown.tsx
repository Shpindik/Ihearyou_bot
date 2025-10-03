import { useState } from 'react';
import { DropdownArrowIcon } from '@/shared/svg';

type Option<T = string> = {
  readonly value: T;
  readonly label: string;
};

type IProps<T = string> = {
  options: readonly Option<T>[];
  placeholder?: string;
  className?: string;
  onSelect?: (option: Option<T>) => void;
};

const Dropdown = <T = string,>({
  options,
  placeholder = 'Выберите вариант',
  className,
  onSelect,
}: IProps<T>) => {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<Option<T> | null>(null);

  return (
    <div className="relative inline-block w-full transition-all ">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className={`${className} w-full flex justify-between items-center px-4 py-2 rounded-full border bg-ui-purple-disabled text-white`}
      >
        <p className="text-lg text-white truncate">
          {selected ? selected.label : placeholder}
        </p>
        <DropdownArrowIcon
          className={`w-4 h-4 ${open ? 'text-ui-purple-primary -rotate-180' : 'text-gray'}`}
        />
      </button>

      {open && (
        <div className="absolute w-full rounded-2xl shadow-lg bg-ui-purple-tertiary bg-purple-secondary">
          <ul className="max-h-60 overflow-y-auto rounded-md ">
            {options.map((opt, index) => (
              <li
                key={index}
                onClick={() => {
                  setSelected(opt);
                  setOpen(false);
                  onSelect?.(opt);
                }}
                className={`px-4 py-2 cursor-pointer hover:bg-ui-purple-primary/10
                    ${selected?.value === opt.value && 'font-medium'}`}
              >
                {opt.label}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Dropdown;

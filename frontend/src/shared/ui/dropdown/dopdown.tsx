import { FC, useState } from 'react';

type Option = {
  value: string;
  label: string;
};

type IProps = {
  options: Option[];
  placeholder?: string;
  className?: string;
};

const Dropdown: FC<IProps> = ({
  options,
  placeholder = 'Выберите вариант',
  className,
}) => {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<Option | null>(null);

  return (
    <div className="relative inline-block w-full">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className={`${className} w-full flex justify-between items-center px-4 py-2 rounded-full border bg-purple-secondary text-black`}
      >
        {selected ? selected.label : placeholder}
        <span className="ml-2">▼</span>
      </button>

      {open && (
        <div className="absolute w-full rounded-2xl shadow-lg bg-dropdown-secondary z-10">
          <ul className="max-h-60 overflow-y-auto rounded-md">
            {options.map((opt) => (
              <li
                key={opt.value}
                onClick={() => {
                  setSelected(opt);
                  setOpen(false);
                }}
                className={`px-4 py-2 cursor-pointer
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

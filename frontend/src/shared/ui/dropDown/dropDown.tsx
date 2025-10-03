import { useState } from "react";

type Option = {
  value: string;
  label: string;
};

type DropdownProps = {
  options: Option[];
  placeholder?: string;
  className?: string;
};

export function Dropdown({ options, placeholder = "Выберите вариант", className }: DropdownProps) {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<Option | null>(null);

  return (
    <div className="relative inline-block w-full">
      {/* Кнопка */}
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className={cn(
          "w-full flex justify-between items-center px-4 py-2 rounded-full border bg-purple-secondary text-black",
          
          className
        )}
      >
        {selected ? selected.label : placeholder}
        <span className="ml-2">▼</span>
      </button>

      {/* Выпадающий список */}
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
                className={cn(
                  "px-4 py-2 cursor-pointer",
                  selected?.value === opt.value && "font-medium"
                )}
              >
                {opt.label}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

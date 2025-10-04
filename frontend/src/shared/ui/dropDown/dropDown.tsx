import { useState } from "react";
// import { DropdownArrowIcon } from "../../svg/dropdown-arrow.icon";

type Option = {
  value: string;
  label: string;
};

type DropdownProps = {
  options: Option[];
  placeholder?: string;
  className?: string;
  icon?: React.ReactNode;
};

export function Dropdown({
  options,
  placeholder = "Выберите вариант",
  className = "",
  
}: DropdownProps) {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<Option | null>(null);

  return (
    <div className="relative inline-block w-full">
      {/* Кнопка */}
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className={`w-full flex justify-between items-center px-4 py-2 rounded-full border bg-purple-secondary text-black ${className}`}
      >
        {selected ? selected.label : placeholder}
        <span className="ml-2">
        
        </span>
      </button>

      {/* Выпадающий список */}
      {open && (
        <div className="absolute rounded-full top-full left-0 right-0">
          <ul className="max-h-60 overflow-y-auto rounded-2xl bg-ui-purple-tertiary" >
            {options.map((opt) => (
              <li
                key={opt.value}
                onClick={() => {
                  setSelected(opt);
                  setOpen(false);
                }}
                className={`px-4 py-2 cursor-pointer ${
                  selected?.value === opt.value ? "font-medium" : ""
                }`}
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

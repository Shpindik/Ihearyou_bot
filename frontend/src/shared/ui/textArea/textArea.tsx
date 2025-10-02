import { ComponentPropsWithoutRef, forwardRef } from "react";


interface TextAreaProps extends ComponentPropsWithoutRef<"textarea"> {
    error?: boolean;
}

 const Textarea = forwardRef<HTMLTextAreaElement, TextAreaProps>({error = false, className = "", placeholder = "Введите текст...", ...props}, ref) => {
  return (
    <textarea
    ref={ref}
      placeholder={placeholder}
      className={`
        w-[392px] h-14 px-6 py-5 rounded-full border resize-none
        focus:outline-none transition-colors
        ${error 
          ? "border-red-500 text-red-error placeholder-red-error " 
          : "border-black text-black placeholder-purple-secondary "}
        ${className}
      `}
    />
  );
};

export default Textarea;
// import { useState } from "react";


interface TextAreaProps {
    placeholder?: string;
    className?: string;
    error?: boolean;
}

 const Textarea = ({ placeholder = "Введите текст...", className = "", error = false }: TextareaProps) => {
    // const [value, setValue] = useState("");
  return (
    <textarea
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

export default TextArea;
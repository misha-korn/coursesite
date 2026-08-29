import { useState } from "react";

import { mediaUrl } from "../api/client.js";

// Простая галерея: крупная картинка плюс миниатюры под ней.
// Используется и на странице курса, и на странице урока.
export default function Gallery({ images }) {
  const [active, setActive] = useState(0);

  if (!images || images.length === 0) return null;

  const current = mediaUrl(images[active]?.image);

  return (
    <div className="space-y-3">
      <img
        src={current}
        alt=""
        className="max-h-96 w-full rounded-xl object-cover"
      />

      {images.length > 1 && (
        <div className="flex flex-wrap gap-2">
          {images.map((item, index) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setActive(index)}
              className={`overflow-hidden rounded-lg border-2 transition ${
                index === active ? "border-brand-600" : "border-transparent opacity-70"
              }`}
            >
              <img src={mediaUrl(item.image)} alt="" className="h-16 w-24 object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

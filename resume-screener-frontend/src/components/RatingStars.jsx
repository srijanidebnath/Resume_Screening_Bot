import { useState } from "react";

export default function RatingStars({ onRate }) {
  const [open, setOpen] = useState(false);
  const [rating, setRating] = useState(0);
  const [submitted, setSubmitted] = useState(false);

  if (submitted) {
    return <span className="hint">Thanks for the feedback.</span>;
  }

  return (
    <div className="bubble-actions">
      {!open && (
        <button className="rate-link" onClick={() => setOpen(true)}>
          Rate this answer
        </button>
      )}
      {open && (
        <div className="stars">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              className={`star-btn ${n <= rating ? "filled" : ""}`}
              onMouseEnter={() => setRating(n)}
              onClick={() => {
                onRate(n);
                setSubmitted(true);
              }}
            >
              ★
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function FeedbackBanner({ tone = "neutral", message }) {
  if (!message) {
    return null;
  }

  return <div className={`feedback-banner feedback-banner--${tone}`}>{message}</div>;
}

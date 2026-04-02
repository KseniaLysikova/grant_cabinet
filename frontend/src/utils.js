export function formatDate(value) {
    if (!value) return "—";
    return new Date(value).toLocaleDateString("ru-RU", {
      year: "numeric",
      month: "long",
      day: "numeric"
    });
  }
  
  export function formatDateTime(value) {
    if (!value) return "—";
    return new Date(value).toLocaleString("ru-RU");
  }
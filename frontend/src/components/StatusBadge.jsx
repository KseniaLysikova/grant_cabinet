const labelMap = {
    draft: "Черновик",
    submitted: "Отправлена",
    in_review: "На рассмотрении",
    approved: "Одобрена",
    rejected: "Отклонена"
  };
  
  export default function StatusBadge({ status }) {
    return <span className={`status-badge status-${status}`}>{labelMap[status] || status}</span>;
  }
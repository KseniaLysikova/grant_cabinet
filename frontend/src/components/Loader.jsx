export default function Loader({ text = "Загрузка...", fullPage = false }) {
    return (
      <div className={fullPage ? "loader-wrap full-page" : "loader-wrap"}>
        <div className="loader" />
        <p>{text}</p>
      </div>
    );
  }
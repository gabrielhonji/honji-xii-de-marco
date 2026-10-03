export const activities = {
  XII: "XII de Março",
  Atleta: "Atleta da XII",
  Hunter: "Hunter E-sports",
  TOC: "TOC Caçadores",
  Pantercats: "Pantercats",
  Panterada: "Bateria Panterada",
  EP: "Engenharíadas Paranaense",
  JIA: "Jogos Interatléticas",
  Evento: "Evento esportivo",
  Social: "Ação social",
};
export type Activity = keyof typeof activities;
export interface Participation {
  id: string;
  name: string;
  ra: string;
  activity: Activity;
  detail: string;
  semester: string;
  hours: number;
  approved: boolean;
  warning: string;
  source: string;
  row: number | string;
}
export type Theme = "light" | "dark";
export const fold = (text: string) =>
  text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .trim();
export const participationKey = (r: Participation) =>
  `${r.ra}|${fold(r.name)}|${r.activity}|${r.semester}|${fold(r.detail)}`;
export const valid = (r: Participation) =>
  Boolean(
    r.name.trim() &&
    r.name.length <= 150 &&
    /^\d{5,12}$/.test(r.ra) &&
    /^20\d{2}\.[12]$/.test(r.semester) &&
    r.detail.trim() &&
    r.detail.length <= 350 &&
    Object.hasOwn(activities, r.activity) &&
    Number.isFinite(r.hours) &&
    r.hours >= 0.5 &&
    r.hours <= 2000,
  );
export const freshParticipation = (): Participation => ({
  id: crypto.randomUUID(),
  name: "",
  ra: "",
  activity: "XII",
  detail: "",
  semester: "",
  hours: 100,
  approved: false,
  warning: "",
  source: "",
  row: "",
});
export const localDate = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

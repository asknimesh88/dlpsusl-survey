import "./globals.css";

export const metadata = {
  title: "Animal Bio-Resource Graduate Survey",
  description:
    "Graduate satisfaction survey results for the Animal Bio-Resource Technology & Management degree, Sabaragamuwa University of Sri Lanka.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

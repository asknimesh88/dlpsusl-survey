import Script from "next/script";
import "./globals.css";

export const metadata = {
  title: "Animal Bio-Resource Graduate Survey",
  description:
    "Graduate satisfaction survey results for the Animal Bio-Resource Technology & Management degree, Sabaragamuwa University of Sri Lanka.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Script id="theme-init" strategy="beforeInteractive">
          {`try{var t=localStorage.getItem("theme");if(t)document.documentElement.setAttribute("data-theme",t);}catch(e){}`}
        </Script>
        {children}
      </body>
    </html>
  );
}

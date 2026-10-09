import "./globals.css";

export const metadata = { title: "Hackathon starter", description: "Demo path" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

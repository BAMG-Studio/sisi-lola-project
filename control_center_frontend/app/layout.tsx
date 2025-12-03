import './globals.css';

export const metadata = {
  title: 'Sisi Lola Control Center',
  description: 'Unified control center for Sisi Lola operations'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

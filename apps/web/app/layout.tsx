import './globals.css'
import { Nav } from '@/components/nav'
export default function RootLayout({ children }: { children: React.ReactNode }) {return <html lang='en'><body><main className='mx-auto max-w-6xl space-y-4 p-6'><header className='card'><h1 className='text-2xl font-semibold'>ApplyForge</h1><p className='text-slate-400'>Your AI Job Hunt Operating System</p><div className='mt-3'><Nav /></div></header>{children}</main></body></html>}

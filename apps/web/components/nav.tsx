import Link from 'next/link'
const links = [['Dashboard','/dashboard'],['Resume','/resume'],['Profile','/profile'],['Jobs','/jobs'],['Applications','/applications'],['Settings','/settings'],['Admin','/admin']]
export function Nav(){return <nav className='flex flex-wrap gap-3 text-sm text-slate-300'>{links.map(([label,href])=><Link key={href} href={href} className='rounded-md border border-slate-700 px-3 py-1 hover:bg-slate-800'>{label}</Link>)}</nav>}

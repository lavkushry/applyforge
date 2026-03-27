'use client'
import { useState } from 'react'
import { api } from '@/lib/api'
export default function ProfilePage(){const [payload,setPayload]=useState('{
  "basics": {"full_name": "Alex Builder"},
  "summary": "Full stack engineer",
  "skills": ["Python","React"]
}'); const [result,setResult]=useState(''); return <section className='card space-y-3'><h2 className='text-xl font-semibold'>Master Profile Editor</h2><textarea className='h-72 w-full rounded bg-slate-800 p-3 font-mono text-sm' value={payload} onChange={(e)=>setPayload(e.target.value)} /><div className='flex gap-2'><button className='rounded border border-slate-600 px-3 py-2' onClick={async()=>{const p=await api('/profile'); setResult(JSON.stringify(p,null,2))}}>Load</button><button className='rounded bg-blue-600 px-3 py-2' onClick={async()=>{try{await api('/profile',{method:'POST',body:payload})}catch{await api('/profile',{method:'PUT',body:payload})}; setResult('Saved')}}>Save</button></div><pre className='rounded bg-slate-950 p-3 text-xs'>{result}</pre></section>}

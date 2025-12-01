import { useStore } from './store/useStore'

function App() {
  // 1. 选择状态 (Selector 模式)
  // 最佳实践：按需选取，避免不必要的重新渲染
  const bears = useStore((state) => state.bears)
  const title = useStore((state) => state.title)
  
  // 2. 获取 Actions
  // 这里的解构也是安全的
  const { increasePopulation, removeAllBears, fetchBears, updateTitle } = useStore()

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>{title}</h1>
      <div className="card">
        <h2>🐻 Bears: {bears}</h2>
        
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginTop: '20px' }}>
          <button onClick={increasePopulation}>
            增加一只熊 (+1)
          </button>
          
          <button onClick={removeAllBears} style={{ backgroundColor: '#ff4d4f' }}>
            清空所有熊
          </button>
          
          <button onClick={fetchBears}>
             异步获取数据 (1s)
          </button>
        </div>

        <div style={{ marginTop: '20px' }}>
            <input 
                value={title} 
                onChange={(e) => updateTitle(e.target.value)} 
                placeholder="修改标题"
                style={{ padding: '8px' }}
            />
        </div>
      </div>
    </div>
  )
}

export default App
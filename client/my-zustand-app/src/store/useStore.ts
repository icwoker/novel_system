import { create } from "zustand";

//1.定义状态和方法
interface BearState {
  bears: number;
  title: string;
  increasePopulation: () => void;
  removeAllBears: () => void;
  updateTitle: (newTitle: string) => void;
  fetchBears: () => Promise<void>;
}

//2.创建Store
export const useStore = create<BearState>((set) => ({
  // ----State(数据)----
  bears: 0,
  title: "Zustan Demo",

  // ---Action(方法) ---
  increasePopulation: () => set((state) => ({ bears: state.bears + 1 })),

  //简单更新:直接设置新值
  removeAllBears: () => set({ bears: 0 }),

  //带参数的更新
  updateTitle: (newTitle) => set({ title: newTitle }),

  //异步Action.直接写async/await即可，不需要Thunk/Saga
  fetchBears: async () => {
    //模拟请求
    const response = await new Promise<number>((resolve) =>
      setTimeout(() => resolve(10), 1000)
    );
    set({ bears: response });
  },
}));

import { useState } from "react";
import { ProfileCard } from "./ProfileCard";
import { Button } from "./ui/button";
import { RotateCcw, Settings } from "lucide-react";

const mockUsers = [
  {
    id: "1",
    name: "Alice",
    age: 28,
    photo: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    bio: "喜欢在图书馆工作，寻找有趣的聊天伙伴。对创业和科技很感兴趣。",
    interests: ["创业", "阅读", "旅行", "摄影"],
    occupation: "产品经理",
    location: "三里屯",
    coffeePreference: "拿铁"
  },
  {
    id: "2",
    name: "David",
    age: 32,
    photo: "https://images.unsplash.com/photo-1594362031308-a8a60a08e654?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMGNvZmZlZXxlbnwxfHx8fDE3NTgzOTE2MzR8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    bio: "金融从业者，热爱咖啡文化。周末喜欢探索新的咖啡店。",
    interests: ["投资", "咖啡", "跑步", "音乐"],
    occupation: "投资顾问",
    location: "国贸",
    coffeePreference: "美式咖啡"
  },
  {
    id: "3",
    name: "Emma",
    age: 25,
    photo: "https://images.unsplash.com/photo-1563722897-e6dac3cec340?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdHVkZW50JTIwY29mZmVlJTIwcmVhZGluZ3xlbnwxfHx8fDE3NTgzOTE2Mzd8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    bio: "设计师，喜欢在安静的咖啡厅画画。寻找能一起探讨艺术的朋友。",
    interests: ["设计", "艺术", "电影", "瑜伽"],
    occupation: "UI设计师",
    location: "望京",
    coffeePreference: "卡布奇诺"
  },
  {
    id: "4",
    name: "Michael",
    age: 29,
    photo: "https://images.unsplash.com/photo-1549299513-83dceea1f48b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMHBlcnNvbiUyMGNhZmV8ZW58MXx8fHwxNzU4MzkxNjQwfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    bio: "咨询师，经常出差。喜欢和不同背景的人交流想法。",
    interests: ["商业", "篮球", "美食", "科技"],
    occupation: "管理咨询师",
    location: "中关村",
    coffeePreference: "手冲咖啡"
  }
];

interface DiscoverPageProps {
  onSettingsClick: () => void;
}

export function DiscoverPage({ onSettingsClick }: DiscoverPageProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [users, setUsers] = useState(mockUsers);

  const handlePass = () => {
    if (currentIndex < users.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      // 重新开始
      setCurrentIndex(0);
    }
  };

  const handleLike = () => {
    // 这里可以添加匹配逻辑
    console.log(`Liked ${users[currentIndex].name}`);
    handlePass();
  };

  const resetCards = () => {
    setCurrentIndex(0);
  };

  const currentUser = users[currentIndex];

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-xl">发现咖啡伙伴</h1>
          <div className="flex gap-2">
            <Button variant="ghost" size="icon" onClick={resetCards}>
              <RotateCcw className="w-5 h-5" />
            </Button>
            <Button variant="ghost" size="icon" onClick={onSettingsClick}>
              <Settings className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Cards Stack */}
        <div className="relative">
          {currentUser ? (
            <ProfileCard 
              key={currentUser.id}
              user={currentUser}
              onPass={handlePass}
              onLike={handleLike}
            />
          ) : (
            <div className="w-full max-w-sm mx-auto bg-card p-8 rounded-lg text-center">
              <h3 className="mb-4">暂时没有更多咖啡伙伴了</h3>
              <p className="text-muted-foreground mb-4">
                稍后再来看看，或者调整你的偏好设置
              </p>
              <Button onClick={resetCards}>
                <RotateCcw className="w-4 h-4 mr-2" />
                重新开始
              </Button>
            </div>
          )}
        </div>

        {/* Progress indicator */}
        <div className="flex justify-center mt-6">
          <div className="flex gap-2">
            {users.map((_, index) => (
              <div 
                key={index}
                className={`w-2 h-2 rounded-full transition-colors ${
                  index <= currentIndex ? 'bg-primary' : 'bg-muted'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
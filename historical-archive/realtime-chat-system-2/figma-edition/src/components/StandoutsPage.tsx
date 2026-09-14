import { ProfileCard } from "./ProfileCard";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Star, Crown, Sparkles } from "lucide-react";
import { useState } from "react";

const standoutUsers = [
  {
    id: "standout1",
    name: "Sophia",
    age: 29,
    photo: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    bio: "咖啡专家，曾在意大利学习咖啡制作。寻找真正懂咖啡的聊天伙伴。",
    interests: ["精品咖啡", "意大利文化", "艺术", "烘焙"],
    occupation: "咖啡师 & 咖啡店老板",
    location: "三里屯",
    coffeePreference: "Single Origin 手冲",
    isStandout: true,
    standoutReason: "Most Compatible"
  },
  {
    id: "standout2", 
    name: "Alexander",
    age: 33,
    photo: "https://images.unsplash.com/photo-1594362031308-a8a60a08e654?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMGNvZmZlZXxlbnwxfHx8fDE3NTgzOTE2MzR8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    bio: "投资人，经常在不同城市的咖啡厅办公。喜欢和有趣的人分享创业故事。",
    interests: ["创投", "创业", "全球咖啡文化", "商业"],
    occupation: "风险投资合伙人",
    location: "国贸",
    coffeePreference: "Espresso",
    isStandout: true,
    standoutReason: "Recently Active"
  }
];

export function StandoutsPage() {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handlePass = () => {
    if (currentIndex < standoutUsers.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handleLike = () => {
    console.log(`Liked standout user ${standoutUsers[currentIndex].name}`);
    handlePass();
  };

  const currentUser = standoutUsers[currentIndex];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-sm border-b p-4">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Star className="w-6 h-6 text-yellow-500" />
              <h1 className="text-xl">Standouts</h1>
            </div>
            <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
              <Crown className="w-3 h-3 mr-1" />
              精选推荐
            </Badge>
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4">
        {/* Info Card */}
        <Card className="p-4 mb-6 bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200">
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-yellow-600 mt-1" />
            <div>
              <h3 className="mb-1 text-yellow-900">每日精选推荐</h3>
              <p className="text-sm text-yellow-700">
                基于你的偏好和活跃度，我们为你精选了最匹配的咖啡伙伴
              </p>
            </div>
          </div>
        </Card>

        {/* Standout Cards */}
        {currentUser ? (
          <div className="relative">
            <div className="absolute -top-2 -right-2 z-10">
              <Badge className="bg-yellow-500 text-white border-2 border-white shadow-lg">
                <Star className="w-3 h-3 mr-1" />
                {currentUser.standoutReason}
              </Badge>
            </div>
            <ProfileCard 
              key={currentUser.id}
              user={currentUser}
              onPass={handlePass}
              onLike={handleLike}
            />
          </div>
        ) : (
          <Card className="p-8 text-center">
            <Star className="w-12 h-12 mx-auto text-yellow-500 mb-4" />
            <h3 className="mb-2">今日精选已看完</h3>
            <p className="text-muted-foreground mb-4">
              明天会有新的精选推荐等着你
            </p>
            <Button variant="outline">
              查看更多推荐
            </Button>
          </Card>
        )}

        {/* Tips */}
        <Card className="p-4 mt-6 bg-blue-50 border-blue-200">
          <h4 className="mb-2 text-blue-900">💡 提示</h4>
          <p className="text-sm text-blue-700">
            Standouts 是根据你的咖啡偏好、兴趣爱好和活跃时间智能推荐的高质量匹配用户
          </p>
        </Card>
      </div>
    </div>
  );
}
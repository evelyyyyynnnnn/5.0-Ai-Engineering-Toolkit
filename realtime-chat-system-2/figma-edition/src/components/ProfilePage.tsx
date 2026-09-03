import { ImageWithFallback } from './figma/ImageWithFallback';
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { MapPin, Briefcase, Coffee, Edit, Camera } from "lucide-react";

interface ProfilePageProps {
  onEditClick: () => void;
}

export function ProfilePage({ onEditClick }: ProfilePageProps) {
  // Mock current user data
  const currentUser = {
    name: "张三",
    age: 26,
    photo: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    bio: "热爱咖啡和深度对话。在科技行业工作，喜欢和有趣的人分享想法和经验。",
    interests: ["科技", "创业", "阅读", "电影", "旅行", "摄影"],
    occupation: "软件工程师",
    location: "朝阳区",
    coffeePreference: "卡布奇诺",
    availableTimes: ["工作日晚上", "周末下午"],
    favoriteSpots: ["三里屯星巴克", "国贸咖啡厅", "望京SOHO咖啡"],
    chatTopics: ["科技趋势", "创业经验", "旅行见闻", "电影推荐"]
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-sm border-b p-4">
        <div className="flex justify-between items-center max-w-md mx-auto">
          <h1 className="text-xl">我的资料</h1>
          <Button variant="ghost" size="icon" onClick={onEditClick}>
            <Edit className="w-5 h-5" />
          </Button>
        </div>
      </div>

      <div className="max-w-md mx-auto p-4 space-y-6">
        {/* Profile Photo */}
        <Card className="p-6">
          <div className="text-center">
            <div className="relative inline-block mb-4">
              <ImageWithFallback
                src={currentUser.photo}
                alt="个人照片"
                className="w-32 h-32 rounded-full object-cover mx-auto"
              />
              <Button 
                size="icon" 
                variant="secondary"
                className="absolute bottom-0 right-0 rounded-full w-8 h-8"
              >
                <Camera className="w-4 h-4" />
              </Button>
            </div>
            <h2 className="mb-2">{currentUser.name}, {currentUser.age}</h2>
            <div className="flex items-center justify-center text-muted-foreground mb-2">
              <MapPin className="w-4 h-4 mr-1" />
              <span className="text-sm">{currentUser.location}</span>
            </div>
            <div className="flex items-center justify-center text-muted-foreground">
              <Briefcase className="w-4 h-4 mr-1" />
              <span className="text-sm">{currentUser.occupation}</span>
            </div>
          </div>
        </Card>

        {/* About Me */}
        <Card className="p-6">
          <h3 className="mb-3">关于我</h3>
          <p className="text-muted-foreground">{currentUser.bio}</p>
        </Card>

        {/* Coffee Preference */}
        <Card className="p-6">
          <div className="flex items-center mb-3">
            <Coffee className="w-5 h-5 mr-2" />
            <h3>咖啡偏好</h3>
          </div>
          <p className="text-muted-foreground">{currentUser.coffeePreference}</p>
        </Card>

        {/* Interests */}
        <Card className="p-6">
          <h3 className="mb-3">兴趣爱好</h3>
          <div className="flex flex-wrap gap-2">
            {currentUser.interests.map((interest, index) => (
              <Badge key={index} variant="secondary">
                {interest}
              </Badge>
            ))}
          </div>
        </Card>

        {/* Available Times */}
        <Card className="p-6">
          <h3 className="mb-3">空闲时间</h3>
          <div className="space-y-2">
            {currentUser.availableTimes.map((time, index) => (
              <div key={index} className="text-sm text-muted-foreground">
                • {time}
              </div>
            ))}
          </div>
        </Card>

        {/* Favorite Coffee Spots */}
        <Card className="p-6">
          <h3 className="mb-3">常去咖啡店</h3>
          <div className="space-y-2">
            {currentUser.favoriteSpots.map((spot, index) => (
              <div key={index} className="text-sm text-muted-foreground">
                • {spot}
              </div>
            ))}
          </div>
        </Card>

        {/* Chat Topics */}
        <Card className="p-6">
          <h3 className="mb-3">聊天话题</h3>
          <div className="flex flex-wrap gap-2">
            {currentUser.chatTopics.map((topic, index) => (
              <Badge key={index} variant="outline">
                {topic}
              </Badge>
            ))}
          </div>
        </Card>

        <Separator />

        {/* Action Buttons */}
        <div className="space-y-3 pb-6">
          <Button className="w-full" onClick={onEditClick}>
            <Edit className="w-4 h-4 mr-2" />
            编辑资料
          </Button>
        </div>
      </div>
    </div>
  );
}
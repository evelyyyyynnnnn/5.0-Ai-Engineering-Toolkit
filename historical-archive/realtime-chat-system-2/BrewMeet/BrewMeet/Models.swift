//
//  Models.swift
//  BrewMeet
//
//  Created by Evelyn Du on 9/20/25.
//

import Foundation

// MARK: - User Model
struct User: Identifiable, Codable {
    let id: String
    let name: String
    let age: Int
    let photo: String
    let bio: String
    let interests: [String]
    let occupation: String
    let location: String
    let coffeePreference: String
    let availableTimes: [String]?
    let favoriteSpots: [String]?
    let chatTopics: [String]?
    let isStandout: Bool?
    let standoutReason: String?
}

// MARK: - Match Model
struct Match: Identifiable, Codable {
    let id: String
    let name: String
    let age: Int
    let photo: String
    let lastMessage: String?
    let timestamp: String
    let unread: Bool
    let location: String
    let status: MatchStatus
    let matchedOn: String
}

enum MatchStatus: String, CaseIterable, Codable {
    case newMatch = "new_match"
    case chatting = "chatting"
    case planning = "planning"
    case scheduled = "scheduled"
    
    var displayName: String {
        switch self {
        case .newMatch:
            return "New Match"
        case .chatting:
            return "Chatting"
        case .planning:
            return "Planning"
        case .scheduled:
            return "Scheduled"
        }
    }
    
    var badgeColor: String {
        switch self {
        case .newMatch:
            return "pink"
        case .chatting:
            return "blue"
        case .planning:
            return "orange"
        case .scheduled:
            return "green"
        }
    }
}

// MARK: - Invitation Model
struct Invitation: Identifiable, Codable {
    let id: String
    let name: String
    let age: Int
    let photo: String
    let message: String
    let timestamp: String
    let location: String
    let suggestedPlace: String
    let suggestedTime: String
    let coffeeType: String
    let interests: [String]
}

// MARK: - Mock Data
class MockData {
    static let users: [User] = [
        User(
            id: "1",
            name: "Alice",
            age: 28,
            photo: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            bio: "I love working in libraries and looking for interesting conversation partners. Very interested in entrepreneurship and technology.",
            interests: ["Entrepreneurship", "Reading", "Travel", "Photography"],
            occupation: "Product Manager",
            location: "Sanlitun",
            coffeePreference: "Latte",
            availableTimes: nil,
            favoriteSpots: nil,
            chatTopics: nil,
            isStandout: nil,
            standoutReason: nil
        ),
        User(
            id: "2",
            name: "David",
            age: 32,
            photo: "https://images.unsplash.com/photo-1594362031308-a8a60a08e654?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMGNvZmZlZXxlbnwxfHx8fDE3NTgzOTE2MzR8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            bio: "Finance professional who loves coffee culture. I enjoy exploring new coffee shops on weekends.",
            interests: ["Investment", "Coffee", "Running", "Music"],
            occupation: "Investment Advisor",
            location: "Guomao",
            coffeePreference: "Americano",
            availableTimes: nil,
            favoriteSpots: nil,
            chatTopics: nil,
            isStandout: nil,
            standoutReason: nil
        ),
        User(
            id: "3",
            name: "Emma",
            age: 25,
            photo: "https://images.unsplash.com/photo-1563722897-e6dac3cec340?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdHVkZW50JTIwY29mZmVlJTIwcmVhZGluZ3xlbnwxfHx8fDE3NTgzOTE2Mzd8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            bio: "Designer who loves drawing in quiet cafes. Looking for friends to discuss art with.",
            interests: ["Design", "Art", "Movies", "Yoga"],
            occupation: "UI Designer",
            location: "Wangjing",
            coffeePreference: "Cappuccino",
            availableTimes: nil,
            favoriteSpots: nil,
            chatTopics: nil,
            isStandout: nil,
            standoutReason: nil
        ),
        User(
            id: "4",
            name: "Michael",
            age: 29,
            photo: "https://images.unsplash.com/photo-1549299513-83dceea1f48b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMHBlcnNvbiUyMGNhZmV8ZW58MXx8fHwxNzU4MzkxNjQwfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            bio: "Consultant who travels frequently. I enjoy exchanging ideas with people from different backgrounds.",
            interests: ["Business", "Basketball", "Food", "Technology"],
            occupation: "Management Consultant",
            location: "Zhongguancun",
            coffeePreference: "Pour Over Coffee",
            availableTimes: nil,
            favoriteSpots: nil,
            chatTopics: nil,
            isStandout: nil,
            standoutReason: nil
        )
    ]
    
    static let standoutUsers: [User] = [
        User(
            id: "standout1",
            name: "Sophia",
            age: 29,
            photo: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            bio: "Coffee expert who studied coffee making in Italy. Looking for conversation partners who truly understand coffee.",
            interests: ["Specialty Coffee", "Italian Culture", "Art", "Baking"],
            occupation: "Barista & Coffee Shop Owner",
            location: "Sanlitun",
            coffeePreference: "Single Origin Pour Over",
            availableTimes: nil,
            favoriteSpots: nil,
            chatTopics: nil,
            isStandout: true,
            standoutReason: "Most Compatible"
        ),
        User(
            id: "standout2",
            name: "Alexander",
            age: 33,
            photo: "https://images.unsplash.com/photo-1594362031308-a8a60a08e654?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMGNvZmZlZXxlbnwxfHx8fDE3NTgzOTE2MzR8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            bio: "Investor who often works from cafes in different cities. I love sharing startup stories with interesting people.",
            interests: ["Venture Capital", "Entrepreneurship", "Global Coffee Culture", "Business"],
            occupation: "Venture Capital Partner",
            location: "Guomao",
            coffeePreference: "Espresso",
            availableTimes: nil,
            favoriteSpots: nil,
            chatTopics: nil,
            isStandout: true,
            standoutReason: "Recently Active"
        )
    ]
    
    static let matches: [Match] = [
        Match(
            id: "match1",
            name: "Olivia",
            age: 28,
            photo: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            lastMessage: "Great! Let's meet at Starbucks in Sanlitun tomorrow at 3 PM ☕",
            timestamp: "Just now",
            unread: true,
            location: "Sanlitun",
            status: .scheduled,
            matchedOn: "2 days ago"
        ),
        Match(
            id: "match2",
            name: "Ryan",
            age: 32,
            photo: "https://images.unsplash.com/photo-1594362031308-a8a60a08e654?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMGNvZmZlZXxlbnwxfHx8fDE3NTgzOTE2MzR8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            lastMessage: "Where is that coffee shop you recommended? I'd like to try it",
            timestamp: "3 hours ago",
            unread: false,
            location: "Guomao",
            status: .chatting,
            matchedOn: "1 week ago"
        ),
        Match(
            id: "match3",
            name: "Zoe",
            age: 26,
            photo: "https://images.unsplash.com/photo-1563722897-e6dac3cec340?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdHVkZW50JTIwY29mZmVlJTIwcmVhZGluZ3xlbnwxfHx8fDE3NTgzOTE2Mzd8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            lastMessage: nil,
            timestamp: "1 day ago",
            unread: false,
            location: "Wangjing",
            status: .newMatch,
            matchedOn: "1 day ago"
        )
    ]
    
    static let invitations: [Invitation] = [
        Invitation(
            id: "inv1",
            name: "Luna",
            age: 27,
            photo: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            message: "Hi! I see you also like pour over coffee. Would you like to meet for coffee and chat about coffee culture?",
            timestamp: "2 hours ago",
            location: "Chaoyang District",
            suggestedPlace: "Blue Bottle Coffee Sanlitun",
            suggestedTime: "Tomorrow 3:00 PM",
            coffeeType: "Pour Over Coffee",
            interests: ["Coffee", "Photography", "Travel"]
        ),
        Invitation(
            id: "inv2",
            name: "Marcus",
            age: 31,
            photo: "https://images.unsplash.com/photo-1594362031308-a8a60a08e654?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMGNvZmZlZXxlbnwxfHx8fDE3NTgzOTE2MzR8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            message: "Hi! I work at a nearby cafe. If you have time, let's grab a coffee together!",
            timestamp: "6 hours ago",
            location: "Guomao",
            suggestedPlace: "Starbucks Guomao",
            suggestedTime: "Weekend 10:30 AM",
            coffeeType: "Latte",
            interests: ["Business", "Technology", "Music"]
        ),
        Invitation(
            id: "inv3",
            name: "Aria",
            age: 25,
            photo: "https://images.unsplash.com/photo-1563722897-e6dac3cec340?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdHVkZW50JTIwY29mZmVlJTIwcmVhZGluZ3xlbnwxfHx8fDE3NTgzOTE2Mzd8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
            message: "I saw your profile and think we have many common topics. I'd like to get to know you and meet for coffee!",
            timestamp: "1 day ago",
            location: "Wangjing",
            suggestedPlace: "% Arabica Wangjing SOHO",
            suggestedTime: "Weekday 7:00 PM",
            coffeeType: "Cappuccino",
            interests: ["Design", "Art", "Movies"]
        )
    ]
    
    static let currentUser = User(
        id: "current",
        name: "Alex",
        age: 26,
        photo: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
        bio: "I love coffee and deep conversations. Working in tech, I enjoy sharing ideas and experiences with interesting people.",
        interests: ["Technology", "Entrepreneurship", "Reading", "Movies", "Travel", "Photography"],
        occupation: "Software Engineer",
        location: "Chaoyang District",
        coffeePreference: "Cappuccino",
        availableTimes: ["Weekday evenings", "Weekend afternoons"],
        favoriteSpots: ["Starbucks Sanlitun", "Guomao Cafe", "Wangjing SOHO Coffee"],
        chatTopics: ["Tech Trends", "Startup Experience", "Travel Stories", "Movie Recommendations"],
        isStandout: nil,
        standoutReason: nil
    )
}

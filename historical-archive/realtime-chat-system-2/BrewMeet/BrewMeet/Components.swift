//
//  Components.swift
//  BrewMeet
//
//  Created by Evelyn Du on 9/20/25.
//

import SwiftUI

// MARK: - Card Component
struct Card<Content: View>: View {
    let content: Content
    
    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }
    
    var body: some View {
        VStack {
            content
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 1)
    }
}

// MARK: - Button Component
struct CustomButton: View {
    let title: String
    let action: () -> Void
    let style: ButtonStyle
    let size: ButtonSize
    
    enum ButtonStyle {
        case primary
        case secondary
        case outline
        case destructive
    }
    
    enum ButtonSize {
        case small
        case medium
        case large
    }
    
    init(_ title: String, style: ButtonStyle = .primary, size: ButtonSize = .medium, action: @escaping () -> Void) {
        self.title = title
        self.style = style
        self.size = size
        self.action = action
    }
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: fontSize, weight: .medium))
                .foregroundColor(textColor)
                .frame(height: height)
                .frame(maxWidth: .infinity)
                .background(backgroundColor)
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(borderColor, lineWidth: borderWidth)
                )
        }
    }
    
    private var fontSize: CGFloat {
        switch size {
        case .small: return 14
        case .medium: return 16
        case .large: return 18
        }
    }
    
    private var height: CGFloat {
        switch size {
        case .small: return 32
        case .medium: return 44
        case .large: return 52
        }
    }
    
    private var backgroundColor: Color {
        switch style {
        case .primary: return Color.black
        case .secondary: return Color.gray.opacity(0.1)
        case .outline: return Color.clear
        case .destructive: return Color.red
        }
    }
    
    private var textColor: Color {
        switch style {
        case .primary: return .white
        case .secondary: return .black
        case .outline: return .black
        case .destructive: return .white
        }
    }
    
    private var borderColor: Color {
        switch style {
        case .primary: return .clear
        case .secondary: return .clear
        case .outline: return .gray
        case .destructive: return .clear
        }
    }
    
    private var borderWidth: CGFloat {
        switch style {
        case .primary: return 0
        case .secondary: return 0
        case .outline: return 1
        case .destructive: return 0
        }
    }
}

// MARK: - Badge Component
struct Badge: View {
    let text: String
    let color: BadgeColor
    
    enum BadgeColor {
        case primary
        case secondary
        case success
        case warning
        case error
        case pink
        case blue
        case green
        case orange
        case warmOrange
    }
    
    init(_ text: String, color: BadgeColor = .secondary) {
        self.text = text
        self.color = color
    }
    
    var body: some View {
        Text(text)
            .font(.system(size: 12, weight: .medium))
            .foregroundColor(textColor)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(backgroundColor)
            .cornerRadius(12)
    }
    
    private var backgroundColor: Color {
        switch color {
        case .primary: return Color.black
        case .secondary: return Color.gray.opacity(0.1)
        case .success: return Color.green.opacity(0.1)
        case .warning: return Color.yellow.opacity(0.1)
        case .error: return Color.red.opacity(0.1)
        case .pink: return Color.pink.opacity(0.1)
        case .blue: return Color.blue.opacity(0.1)
        case .green: return Color.green.opacity(0.1)
        case .orange: return Color.orange.opacity(0.1)
        case .warmOrange: return Color.orange.opacity(0.15)
        }
    }
    
    private var textColor: Color {
        switch color {
        case .primary: return .white
        case .secondary: return .black
        case .success: return .green
        case .warning: return .orange
        case .error: return .red
        case .pink: return .pink
        case .blue: return .blue
        case .green: return .green
        case .orange: return .orange
        case .warmOrange: return .orange
        }
    }
}

// MARK: - Profile Card Component
struct ProfileCard: View {
    let user: User
    let onPass: () -> Void
    let onLike: () -> Void
    
    @Environment(\.horizontalSizeClass) var horizontalSizeClass
    @Environment(\.verticalSizeClass) var verticalSizeClass
    
    var body: some View {
        let isCompact = horizontalSizeClass == .compact
        
        VStack(spacing: 0) {
            // Photo
            AsyncImage(url: URL(string: user.photo)) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
            }
            .frame(height: isCompact ? 280 : 320)
            .clipped()
            
            // Content area
            VStack(alignment: .leading, spacing: isCompact ? 12 : 16) {
                // Occupation
                HStack(spacing: isCompact ? 6 : 8) {
                    Image(systemName: "briefcase.fill")
                        .font(.system(size: isCompact ? 14 : 16))
                        .foregroundColor(.black)
                    
                    Text(user.occupation)
                        .font(.system(size: isCompact ? 14 : 16))
                        .foregroundColor(.black)
                }
                
                // Coffee preference
                HStack(spacing: isCompact ? 6 : 8) {
                    Image(systemName: "cup.and.saucer.fill")
                        .font(.system(size: isCompact ? 14 : 16))
                        .foregroundColor(.black)
                    
                    Text("Preference: \(user.coffeePreference)")
                        .font(.system(size: isCompact ? 14 : 16))
                        .foregroundColor(.black)
                }
                
                // Bio
                Text(user.bio)
                    .font(.system(size: isCompact ? 12 : 14))
                    .foregroundColor(.black)
                    .lineLimit(3)
                    .multilineTextAlignment(.leading)
                
                // Interests
                HStack(spacing: isCompact ? 6 : 8) {
                    ForEach(user.interests.prefix(3), id: \.self) { interest in
                        Badge(interest, color: .secondary)
                    }
                    Spacer()
                }
            }
            .padding(isCompact ? 16 : 20)
            .background(Color.white)
            
            // Action buttons - centered
            HStack(spacing: isCompact ? 12 : 16) {
                Button(action: onPass) {
                    HStack {
                        Image(systemName: "xmark")
                            .font(.system(size: isCompact ? 18 : 20, weight: .bold))
                        Text("Pass")
                            .font(.system(size: isCompact ? 14 : 16, weight: .medium))
                    }
                    .foregroundColor(.black)
                    .frame(height: isCompact ? 44 : 50)
                    .frame(maxWidth: .infinity)
                    .background(Color.white)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.black, lineWidth: 2)
                    )
                    .cornerRadius(8)
                }
                
                Button(action: onLike) {
                    HStack {
                        Image(systemName: "heart.fill")
                            .font(.system(size: isCompact ? 18 : 20, weight: .bold))
                        Text("Meet")
                            .font(.system(size: isCompact ? 14 : 16, weight: .medium))
                    }
                    .foregroundColor(.white)
                    .frame(height: isCompact ? 44 : 50)
                    .frame(maxWidth: .infinity)
                    .background(Color.black)
                    .cornerRadius(8)
                }
            }
            .padding(.horizontal, isCompact ? 16 : 20)
            .padding(.bottom, isCompact ? 16 : 20)
            .background(Color.white)
        }
        .background(Color.white)
        .cornerRadius(16)
    }
}

// MARK: - Async Image with Fallback
struct AsyncImageWithFallback: View {
    let url: String
    let placeholder: String
    let contentMode: ContentMode
    
    init(url: String, placeholder: String = "person.circle.fill", contentMode: ContentMode = .fit) {
        self.url = url
        self.placeholder = placeholder
        self.contentMode = contentMode
    }
    
    var body: some View {
        AsyncImage(url: URL(string: url)) { image in
            image
                .resizable()
                .aspectRatio(contentMode: contentMode)
        } placeholder: {
            Image(systemName: placeholder)
                .font(.system(size: 40))
                .foregroundColor(.gray)
        }
    }
}

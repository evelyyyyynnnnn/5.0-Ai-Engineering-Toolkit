//
//  FilterComponents.swift
//  BrewMeet
//
//  Created by Evelyn Du on 9/20/25.
//

import SwiftUI

// MARK: - Filter Components

struct FilterChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 4) {
                Text(title)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(isSelected ? .white : .black)
                
                Image(systemName: "chevron.down")
                    .font(.system(size: 10, weight: .medium))
                    .foregroundColor(isSelected ? .white : .black)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(isSelected ? Color.black : Color.white)
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(Color.black, lineWidth: 1)
            )
            .cornerRadius(16)
        }
    }
}

// MARK: - Enhanced Profile Components

struct EnhancedProfileCard: View {
    let user: User
    let onPass: () -> Void
    let onLike: () -> Void
    
    var body: some View {
        VStack(spacing: 0) {
            // Profile photo with overlay
            ZStack(alignment: .bottomTrailing) {
                AsyncImageWithFallback(
                    url: user.photo,
                    contentMode: .fill
                )
                .frame(height: 400)
                .clipped()
                
                // Like button on photo
                Button(action: onLike) {
                    Image(systemName: "heart.fill")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.white)
                        .frame(width: 50, height: 50)
                        .background(Color.black.opacity(0.7))
                        .clipShape(Circle())
                }
                .padding(.trailing, 16)
                .padding(.bottom, 16)
            }
            
            // Profile info
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("\(user.name), \(user.age)")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.black)
                        
                        HStack(spacing: 8) {
                            Image(systemName: "location.fill")
                                .font(.system(size: 14))
                                .foregroundColor(.gray)
                            Text(user.location)
                                .font(.system(size: 16))
                                .foregroundColor(.gray)
                        }
                    }
                    
                    Spacer()
                    
                    // Action buttons
                    HStack(spacing: 16) {
                        Button(action: onPass) {
                            Image(systemName: "xmark")
                                .font(.system(size: 20, weight: .bold))
                                .foregroundColor(.black)
                                .frame(width: 50, height: 50)
                                .background(Color.white)
                                .clipShape(Circle())
                                .overlay(
                                    Circle()
                                        .stroke(Color.black, lineWidth: 2)
                                )
                        }
                        
                        Button(action: onLike) {
                            Image(systemName: "heart.fill")
                                .font(.system(size: 20, weight: .bold))
                                .foregroundColor(.white)
                                .frame(width: 50, height: 50)
                                .background(Color.black)
                                .clipShape(Circle())
                        }
                    }
                }
            }
            .padding(16)
            .background(Color.white)
        }
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 4, x: 0, y: 2)
    }
}

struct ProfileDetailsCard: View {
    let user: User
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("About Me")
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.black)
            
            Text(user.bio)
                .font(.system(size: 16))
                .foregroundColor(.gray)
                .lineSpacing(4)
            
            HStack {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: "briefcase.fill")
                            .font(.system(size: 16))
                            .foregroundColor(.black)
                        Text("Occupation")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.black)
                    }
                    Text(user.occupation)
                        .font(.system(size: 14))
                        .foregroundColor(.gray)
                }
                
                Spacer()
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 1)
    }
}

struct CoffeePreferencesCard: View {
    let user: User
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Image(systemName: "cup.and.saucer.fill")
                    .font(.system(size: 18))
                    .foregroundColor(.black)
                Text("Coffee Preferences")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.black)
            }
            
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("Favorite Coffee:")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.black)
                    Spacer()
                    Text(user.coffeePreference)
                        .font(.system(size: 16))
                        .foregroundColor(.gray)
                }
                
                if let spots = user.favoriteSpots, !spots.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Favorite Coffee Shops:")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.black)
                        
                        ForEach(spots, id: \.self) { spot in
                            HStack {
                                Text("•")
                                    .font(.system(size: 14))
                                    .foregroundColor(.gray)
                                Text(spot)
                                    .font(.system(size: 14))
                                    .foregroundColor(.gray)
                            }
                        }
                    }
                }
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 1)
    }
}

struct InterestsCard: View {
    let user: User
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Interests & Topics")
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.black)
            
            // Interests
            VStack(alignment: .leading, spacing: 8) {
                Text("Interests:")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.black)
                
                LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 8) {
                    ForEach(user.interests, id: \.self) { interest in
                        Badge(interest, color: .secondary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
            }
            
            // Chat topics
            if let topics = user.chatTopics, !topics.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Chat Topics:")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.black)
                    
                    LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 8) {
                        ForEach(topics, id: \.self) { topic in
                            Badge(topic, color: .blue)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                }
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 1)
    }
}

// MARK: - Filter Page View

struct FilterPageView: View {
    @Environment(\.presentationMode) var presentationMode
    @Binding var selectedFilters: [String]
    
    private let coffeeTypes = ["Espresso", "Americano", "Latte", "Cappuccino", "Pour Over", "Cold Brew"]
    private let ageRanges = ["18-25", "26-35", "36-45", "46-55", "55+"]
    private let distances = ["1 mile", "5 miles", "10 miles", "25 miles", "50+ miles"]
    private let availabilities = ["Morning", "Afternoon", "Evening", "Weekend"]
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    // Coffee Type
                    FilterSection(title: "Coffee Type", options: coffeeTypes, selectedFilters: $selectedFilters)
                    
                    // Age Range
                    FilterSection(title: "Age Range", options: ageRanges, selectedFilters: $selectedFilters)
                    
                    // Distance
                    FilterSection(title: "Distance", options: distances, selectedFilters: $selectedFilters)
                    
                    // Availability
                    FilterSection(title: "Availability", options: availabilities, selectedFilters: $selectedFilters)
                }
                .padding()
            }
            .navigationTitle("Filters")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                leading: Button("Clear All") {
                    selectedFilters.removeAll()
                },
                trailing: Button("Done") {
                    presentationMode.wrappedValue.dismiss()
                }
            )
        }
    }
}

struct FilterSection: View {
    let title: String
    let options: [String]
    @Binding var selectedFilters: [String]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.black)
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 8) {
                ForEach(options, id: \.self) { option in
                    FilterOptionChip(
                        title: option,
                        isSelected: selectedFilters.contains(option)
                    ) {
                        toggleOption(option)
                    }
                }
            }
        }
    }
    
    private func toggleOption(_ option: String) {
        if selectedFilters.contains(option) {
            selectedFilters.removeAll { $0 == option }
        } else {
            selectedFilters.append(option)
        }
    }
}

struct FilterOptionChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(isSelected ? .white : .black)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(isSelected ? Color.black : Color.white)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.black, lineWidth: 1)
                )
                .cornerRadius(8)
        }
    }
}
